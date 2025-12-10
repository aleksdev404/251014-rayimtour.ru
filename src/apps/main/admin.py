from django.contrib import admin
from django.utils.html import format_html

from . import models


@admin.register(models.SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Брендинг", {"fields": ("logo", "logo_preview", "slogan", "copyright_text", "tursab_image", "tursab_preview")}),  # noqa
        ("Контакты", {"fields": (
            "address",
            "address_gmap",
            "email",
            "phone",
            "phone_repr",
            "whatsapp",
            "whatsapp_repr"
        )}),
        (
            "Баннер",
            {
                "fields": (
                    "banner_link",
                    "banner_image"
                )
            }
        )
    )
    readonly_fields = ("logo_preview", "tursab_preview")
    list_display = ("__str__", "email", "phone", "whatsapp")

    def has_add_permission(self, request):
        if models.SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height:60px;"/>', obj.logo.url)  # noqa
        return "—"
    logo_preview.short_description = "Логотип (превью)"

    def tursab_preview(self, obj):
        if obj.tursab_image:
            return format_html('<img src="{}" style="max-height:60px;"/>', obj.tursab_image.url)  # noqa
        return "—"
    tursab_preview.short_description = "Турсаб (превью)"


class ExcursionImageInline(admin.TabularInline):
    model = models.ExcursionImage
    extra = 1
    fields = ("image", "caption", "sort_order", "thumb")
    readonly_fields = ("thumb",)

    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:60px;"/>', obj.image.url)  # noqa
        return "—"
    thumb.short_description = "Превью"


@admin.register(models.Excursion)
class ExcursionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("title", "slug", "is_published")}),
        ("Контент", {"fields": ("short_description", "content_md")}),
        ("Изображения", {"fields": ("cover", "cover_thumb", "cover_head", "cover_head_thumb")}),  # noqa
    )
    inlines = (ExcursionImageInline,)
    list_display = ("title", "is_published", "created_at", "updated_at", "cover_thumb")  # noqa
    list_filter = ("is_published", "created_at")
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ("cover_thumb", "cover_head_thumb")
    search_fields = ("title", "short_description", "content_md")

    def cover_thumb(self, obj):
        if obj.cover:
            return format_html('<img src="{}" style="max-height:60px;"/>', obj.cover.url)  # noqa
        return "—"

    def cover_head_thumb(self, obj):
        if obj.cover_head:
            return format_html('<img src="{}" style="max-height:60px;"/>', obj.cover_head.url)  # noqa
        return "—"

    cover_thumb.short_description = "Превью"


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("full_name", "is_published", "created_at", "photo_thumb")
    list_filter = ("is_published", "created_at")
    search_fields = ("full_name", "text")
    readonly_fields = ("photo_thumb",)
    fields = ("full_name", "text", "is_published", "photo", "photo_thumb")

    def photo_thumb(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height:60px;"/>', obj.photo.url)  # noqa
        return "—"
    photo_thumb.short_description = "Превью"


@admin.register(models.FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "is_published", "sort_order")
    list_editable = ("is_published", "sort_order")
    search_fields = ("question", "answer")
    ordering = ("sort_order", "id")


@admin.register(models.SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "fa_icon", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    search_fields = ("title", "url", "fa_icon")
    ordering = ("sort_order", "id")
