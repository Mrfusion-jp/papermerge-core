from django.test import TestCase

from papermerge.core.models import Document, User
from papermerge.core.serializers.node import (
    NodesDownloadSerializer,
    TARGZ
)
from papermerge.core.nodes_download import (
    get_nodes_download,
    NodesDownloadDocument,
    NodesDownloadZip,
    NodesDownloadTarGz
)


class TestNodesDownload(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1")
        self.doc = Document.objects.create_document(
            title="invoice.pdf",
            lang="deu",
            user_id=self.user.pk,
            parent=self.user.home_folder
        )

    def test_get_nodes_download_with_one_node(self):
        """
        Asserts that given a list with one item in node_ids
        `get_nodes_download` will return an instance of
        NodesDownloadDocument class
        """
        download = get_nodes_download(
            node_ids=[self.doc.id]
        )
        self.assertTrue(
            isinstance(download, NodesDownloadDocument)
        )

    def test_get_nodes_download_with_multiple_nodes_zip(self):
        """
        Asserts that given a list with multiple items in node_ids
        `get_nodes_download` will return (by default)
        an instance of NodesDownloadZip class
        """
        download = get_nodes_download(
            node_ids=[101, 100]
        )
        self.assertTrue(
            isinstance(download, NodesDownloadZip)
        )

    def test_get_nodes_download_with_multiple_nodes_tar(self):
        """
        Asserts that given a list with multiple items in node_ids
        and archive_type argument set to 'targz' `get_nodes_download`
        will return  an instance of NodesDownloadTarGz class
        """
        download = get_nodes_download(
            node_ids=[101, 100],
            archive_type=TARGZ
        )
        self.assertTrue(
            isinstance(download, NodesDownloadTarGz)
        )

    def test_get_nodes_download_used_with_serializer(self):
        serializer = NodesDownloadSerializer(
            data={
                'node_ids': [self.doc.id],
                'file_name': 'invoice.pdf'
            }
        )
        if serializer.is_valid():
            download = get_nodes_download(
                node_ids=serializer.data['node_ids'],
                file_name=serializer.data['file_name'],
            )
            self.assertEqual(download.file_name, 'invoice.pdf')
            self.assertTrue(
                isinstance(download, NodesDownloadDocument)
            )
        else:
            # should never reach this place as serialized data is
            # expected to be valid
            self.assertTrue(False)
