using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
using System.Text.Json;

if (args.Length < 2 || (args[0] != "positive" && args[0] != "negative"))
{
    Console.Error.WriteLine("Usage: TlsProbe positive|negative https://host/ [...]");
    return 2;
}

bool passed = true;
foreach (string url in args.Skip(1))
{
    string result = "inconclusive";
    string detail;
    SslPolicyErrors? policyErrors = null;
    X509ChainStatusFlags chainErrors = X509ChainStatusFlags.NoError;
    string? peerSha256 = null;
    using var handler = new HttpClientHandler { AllowAutoRedirect = false };
    // Record platform verification results while retaining strict TLS validation.
    handler.ServerCertificateCustomValidationCallback = (_, certificate, chain, errors) =>
    {
        peerSha256 = certificate?.GetCertHashString(System.Security.Cryptography.HashAlgorithmName.SHA256).ToLowerInvariant();
        policyErrors = errors;
        if (chain != null)
        {
            foreach (var status in chain.ChainStatus)
                chainErrors |= status.Status;
        }
        return errors == SslPolicyErrors.None;
    };
    using var client = new HttpClient(handler) { Timeout = TimeSpan.FromSeconds(15) };
    try
    {
        var uri = new Uri(url);
        if (uri.Scheme != Uri.UriSchemeHttps || !string.IsNullOrEmpty(uri.UserInfo))
            throw new ArgumentException("Expected an HTTPS URL without credentials");
        using var response = await client.GetAsync(uri, HttpCompletionOption.ResponseHeadersRead);
        result = "accepted";
        detail = $"HTTP {(int)response.StatusCode}";
    }
    catch (Exception failure)
    {
        const X509ChainStatusFlags expectedTrustErrors = X509ChainStatusFlags.UntrustedRoot
            | X509ChainStatusFlags.PartialChain | X509ChainStatusFlags.Revoked;
        if (policyErrors == SslPolicyErrors.RemoteCertificateChainErrors
            && (chainErrors & expectedTrustErrors) != 0
            && (chainErrors & ~expectedTrustErrors) == 0)
            result = "rejected";
        detail = $"{failure.GetType().Name}: {failure.Message}; policy={policyErrors}; chain={chainErrors}";
    }
    passed &= args[0] == "positive" ? result == "accepted" : result == "rejected";
    Console.WriteLine(JsonSerializer.Serialize(new { url, expected = args[0], result, detail, peerSha256 }));
}
return passed ? 0 : 1;
