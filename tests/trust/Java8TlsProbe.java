import java.net.URI;
import java.net.Socket;
import javax.net.ssl.HttpsURLConnection;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.security.cert.CertPathBuilderException;
import java.security.cert.CertPathValidatorException;
import java.security.cert.CertificateExpiredException;
import java.security.cert.CertificateNotYetValidException;
import java.security.cert.PKIXReason;
import java.security.KeyStore;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLEngine;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509ExtendedTrustManager;

/** Tests the JVM's default TLS trust without credentials or trust overrides. */
public final class Java8TlsProbe {
    private static final class ObservedTrust extends X509ExtendedTrustManager {
        private final X509ExtendedTrustManager delegate;
        private volatile boolean invalidDates;
        private final List<String> peerSha256 = new ArrayList<>();

        ObservedTrust() throws Exception {
            TrustManagerFactory factory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
            factory.init((KeyStore) null);
            X509ExtendedTrustManager selected = null;
            for (TrustManager manager : factory.getTrustManagers()) {
                if (manager instanceof X509ExtendedTrustManager) {
                    selected = (X509ExtendedTrustManager) manager;
                    break;
                }
            }
            if (selected == null) {
                throw new IllegalStateException("No default extended X.509 trust manager");
            }
            delegate = selected;
        }

        private void observeDates(X509Certificate[] chain) {
            peerSha256.clear();
            for (X509Certificate certificate : chain) {
                try {
                    byte[] digest = MessageDigest.getInstance("SHA-256").digest(certificate.getEncoded());
                    StringBuilder hex = new StringBuilder();
                    for (byte value : digest) { hex.append(String.format("%02x", value & 0xff)); }
                    peerSha256.add(hex.toString());
                    certificate.checkValidity();
                } catch (Exception failure) {
                    invalidDates = true;
                }
            }
        }

        public X509Certificate[] getAcceptedIssuers() { return delegate.getAcceptedIssuers(); }
        public void checkClientTrusted(X509Certificate[] chain, String authType) throws CertificateException {
            delegate.checkClientTrusted(chain, authType);
        }
        public void checkClientTrusted(X509Certificate[] chain, String authType, Socket socket) throws CertificateException {
            delegate.checkClientTrusted(chain, authType, socket);
        }
        public void checkClientTrusted(X509Certificate[] chain, String authType, SSLEngine engine) throws CertificateException {
            delegate.checkClientTrusted(chain, authType, engine);
        }
        public void checkServerTrusted(X509Certificate[] chain, String authType) throws CertificateException {
            observeDates(chain);
            delegate.checkServerTrusted(chain, authType);
        }
        public void checkServerTrusted(X509Certificate[] chain, String authType, Socket socket) throws CertificateException {
            observeDates(chain);
            delegate.checkServerTrusted(chain, authType, socket);
        }
        public void checkServerTrusted(X509Certificate[] chain, String authType, SSLEngine engine) throws CertificateException {
            observeDates(chain);
            delegate.checkServerTrusted(chain, authType, engine);
        }
    }

    private static String json(String value) {
        return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"")
                .replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t") + "\"";
    }

    private static String jsonArray(List<String> values) {
        StringBuilder out = new StringBuilder("[");
        for (String value : values) {
            if (out.length() > 1) { out.append(","); }
            out.append(json(value));
        }
        return out.append("]").toString();
    }

    private static boolean isTrustRejection(Throwable failure) {
        boolean rejected = false;
        for (Throwable cause = failure; cause != null; cause = cause.getCause()) {
            if (cause instanceof CertificateExpiredException
                    || cause instanceof CertificateNotYetValidException) {
                return false;
            }
            if (cause instanceof CertPathBuilderException) {
                rejected = true;
            }
            if (cause instanceof CertPathValidatorException) {
                CertPathValidatorException.Reason reason =
                        ((CertPathValidatorException) cause).getReason();
                if (reason == PKIXReason.NO_TRUST_ANCHOR
                        || reason == CertPathValidatorException.BasicReason.REVOKED) {
                    rejected = true;
                } else {
                    return false;
                }
            }
        }
        return rejected;
    }

    public static void main(String[] args) {
        if (args.length < 2 || !(args[0].equals("positive") || args[0].equals("negative"))) {
            System.err.println("Usage: Java8TlsProbe positive|negative https://host/ [...]");
            System.exit(2);
        }
        boolean passed = true;
        for (int index = 1; index < args.length; index++) {
            String result = "inconclusive";
            String detail;
            ObservedTrust trust = null;
            try {
                URI uri = URI.create(args[index]);
                if (!"https".equals(uri.getScheme()) || uri.getUserInfo() != null) {
                    throw new IllegalArgumentException("Expected an HTTPS URL without credentials");
                }
                trust = new ObservedTrust();
                SSLContext context = SSLContext.getInstance("TLS");
                context.init(null, new TrustManager[]{trust}, null);
                HttpsURLConnection connection = (HttpsURLConnection) uri.toURL().openConnection();
                connection.setSSLSocketFactory(context.getSocketFactory());
                connection.setConnectTimeout(10000);
                connection.setReadTimeout(15000);
                connection.setInstanceFollowRedirects(false);
                connection.setRequestMethod("GET");
                try {
                    int status = connection.getResponseCode();
                    result = "accepted";
                    detail = "HTTP " + status;
                } finally {
                    connection.disconnect();
                }
            } catch (Exception failure) {
                if (trust != null && !trust.invalidDates && isTrustRejection(failure)) {
                    result = "rejected";
                }
                detail = failure.getClass().getName() + ": " + failure.getMessage()
                        + (trust != null && trust.invalidDates ? "; expired or not-yet-valid peer certificate" : "");
            }
            passed &= args[0].equals("positive") ? result.equals("accepted") : result.equals("rejected");
            System.out.println("{\"url\":" + json(args[index]) + ",\"expected\":" + json(args[0])
                    + ",\"result\":" + json(result) + ",\"detail\":" + json(detail)
                    + ",\"peer_sha256\":" + jsonArray(trust == null ? new ArrayList<String>() : trust.peerSha256) + "}");
        }
        if (!passed) {
            System.exit(1);
        }
    }
}
