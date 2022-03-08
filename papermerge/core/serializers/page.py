from rest_framework import serializers as rest_serializers
from rest_framework_json_api import serializers
from papermerge.core.models import (
    Page
)


class PageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Page
        resource_name = 'pages'
        fields = (
            'id',
            'number',
            'text',
            'lang',
            'document_version',
        )


class PageDeleteSerializer(rest_serializers.Serializer):
    # list of pages to delete
    pages = rest_serializers.ListField(
        child=rest_serializers.CharField()
    )


class PageReorderSerializer(rest_serializers.Serializer):
    id = rest_serializers.CharField(max_length=32)
    old_number = rest_serializers.IntegerField()
    new_number = rest_serializers.IntegerField()


class PagesReorderSerializer(rest_serializers.Serializer):
    pages = PageReorderSerializer(many=True)


class PageRotateSerializer(rest_serializers.Serializer):
    id = rest_serializers.CharField(max_length=32)
    # rotation angle
    angle = rest_serializers.IntegerField()


class PagesRotateSerializer(rest_serializers.Serializer):
    pages = PageRotateSerializer(many=True)


class PageIdSerializer(rest_serializers.Serializer):
    id = rest_serializers.CharField(max_length=32)


class PagesMoveToFolderSerializer(rest_serializers.Serializer):
    pages = PageIdSerializer(many=True)
    # destination folder node
    dst = rest_serializers.CharField(max_length=32)
    single_page = rest_serializers.BooleanField(default=False)


class PagesMoveToDocumentSerializer(rest_serializers.Serializer):
    pages = PageIdSerializer(many=True)
    # destination document node
    dst = rest_serializers.CharField(max_length=32)
    position = rest_serializers.IntegerField(default=-1)
