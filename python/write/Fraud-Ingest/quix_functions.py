from quixstreaming import StreamWriter


class QuixFunctions:

    def __init__(self, stream_writer: StreamWriter):
        self.stream_writer = stream_writer

    def data_handler(self, dataset):
        # Write Data to Stream
        self.stream_writer.parameters.write(dataset)
        self.stream_writer.parameters.flush()

