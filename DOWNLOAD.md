Dataset **Coffee Leaf Biotic Stress** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/remote/eyJsaW5rIjogImZzOi8vYXNzZXRzLzkwM19Db2ZmZWUgTGVhZiBCaW90aWMgU3RyZXNzL2NvZmZlZS1sZWFmLWJpb3RpYy1zdHJlc3MtRGF0YXNldE5pbmphLnRhciIsICJzaWciOiAiQjBCUkVNL1Z4YkY3ZUVab3I3Yi80YTNxS3pCN3lITjh4U2huRE1TRXc4az0ifQ==)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='Coffee Leaf Biotic Stress', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be [downloaded here](https://drive.google.com/open?id=15YHebAGrx1Vhv8-naave-R5o3Uo70jsm).