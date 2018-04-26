class Decoder:
    def __init__(self, dst_enc):
        self.dst_enc = dst_enc

    def process(self,X ):
        src_enc = self._detect(X)
        return self._decode(X, src_enc)

    def _detect(self, X):
        pass

    def _decode(self, X, src_enc):
        return X
