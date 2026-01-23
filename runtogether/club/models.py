from django.db import models
from django_editorjs_fields import EditorJsJSONField


class Club(models.Model):
    name = models.CharField(max_length=500, null=False, blank=False)
    description = EditorJsJSONField(
        # https://github.com/editor-js/awesome-editorjs?tab=readme-ov-file
        # plugins=[
        #     "@editorjs/image",
        #     "header-with-alignment",
        #     "paragraph-with-alignment",
        #     "@cychann/editorjs-quote",
        #     "@editorjs/warning",
        #     "@coolbytes/editorjs-delimiter",
        #     "editorjs-alert",
        #     "editorjs-color-picker",
        #     "@skchawala/editorjs-text-style",
        #     "@editorjs/list@latest",
        #     "@editorjs/nested-list",
        #     "@editorjs/image",
        #     "@editorjs/simple-image",
        #     "@editorjs/link@editorjs/table",
        #     "editorjs-hyperlink",
        # ],
        # tools={
        #     "Image": {
        #         "config": {
        #             "endpoints": {
        #                 "byFile": "/editorjs/image_upload/"  # Your custom backend file uploader endpoint
        #             }
        #         }
        #     },
        # },
        # i18n={
        #     "messages": {
        #         "blockTunes": {
        #             "delete": {"Delete": "Удалить"},
        #             "moveUp": {"Move up": "Переместить вверх"},
        #             "moveDown": {"Move down": "Переместить вниз"},
        #         }
        #     },
        # },
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    members = models.ManyToManyField("accounts.User", through="relation.ClubMembership", related_name="clubs")
    city = models.ForeignKey(
        "city.City",
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        related_name="clubs",
        help_text="City where the user resides",
    )
