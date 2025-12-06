from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.urls import reverse

from io import BytesIO
from pathlib import Path
from PIL import Image


def upload_to(instance, filename):
    """
    Формирует путь для загрузки файлов:
    <app>/<model>/<field>/<filename>
    Пример: core/excursion/cover/image.jpg
    """
    app_label = instance._meta.app_label
    model_name = instance.__class__.__name__.lower()

    # Пытаемся определить имя поля, вызвавшего upload_to
    field_name = None
    for field in instance._meta.fields:
        if getattr(field, "upload_to", None) == upload_to:
            field_name = field.name
            break

    field_name = field_name or "file"

    return f"{app_label}/{model_name}/{field_name}/{filename}"


class ImageCompressionMixin:
    image_field_name = "cover"   # имя поля по умолчанию
    max_width = 1280
    max_height = 1280
    quality = 70

    def compress_image(self):
        field = getattr(self, self.image_field_name)

        if not field:
            return

        img = Image.open(field)

        if img.mode != "RGB":
            img = img.convert("RGB")

        img.thumbnail((self.max_width, self.max_height))

        img_io = BytesIO()
        img.save(img_io, format="JPEG", quality=self.quality, optimize=True)
        img_io.seek(0)

        original_name = Path(field.name).stem
        new_name = f"{original_name}.jpg"

        compressed_file = InMemoryUploadedFile(
            img_io,
            field_name="ImageField",
            name=new_name,
            content_type="image/jpeg",
            size=img_io.getbuffer().nbytes,
            charset=None
        )

        setattr(self, self.image_field_name, compressed_file)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.compress_image()
        super().save(update_fields=[self.image_field_name])


class SiteSettings(models.Model):
    logo = models.ImageField("Логотип", upload_to=upload_to, blank=True, null=True)  # noqa
    slogan = models.CharField("Слоган", max_length=255, blank=True)
    copyright_text = models.CharField("Текст копирайт", max_length=255, blank=True)  # noqa
    tursab_image = models.ImageField("Изображение Турсаб", upload_to=upload_to, blank=True, null=True)  # noqa

    address = models.CharField("Адрес", max_length=255, blank=True)
    email = models.EmailField("Почта", blank=True)
    phone = models.CharField("Номер телефона", max_length=50, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=50, blank=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"

    def save(self, *args, **kwargs):
        # У всех синглтонов будет pk = 1
        if not self.pk:
            # Если уже есть объект в БД – не даём создать второй
            if self.__class__.objects.exists():
                raise ValidationError("Экземпляр этой модели уже существует")
            self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        # Вернёт существующий объект или создаст новый (pk=1)
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Excursion(
    ImageCompressionMixin,
    models.Model
):
    title = models.CharField("Название", max_length=200)
    slug = models.SlugField(unique=True, null=False)
    short_description = models.TextField("Короткое описание", blank=True)
    content_md = models.TextField("Контент (Markdown, без изображений)", blank=True)  # noqa

    is_published = models.BooleanField("Опубликовано", default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)  # noqa
    updated_at = models.DateTimeField("Обновлено", auto_now=True)  # noqa

    cover = models.ImageField("Изображение (обложка)", upload_to=upload_to, blank=True, null=True)  # noqa
    image_field_name = "cover"
    max_width = 1280
    max_height = 1280
    quality = 75

    class Meta:
        verbose_name = "Экскурсия"
        verbose_name_plural = "Экскурсии"
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('main:excursion-detail', kwargs={'slug': self.slug})


class ExcursionImage(
    ImageCompressionMixin,
    models.Model
):
    excursion = models.ForeignKey(
        Excursion,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Экскурсия",
    )
    caption = models.CharField("Подпись", max_length=200, blank=True)
    sort_order = models.PositiveIntegerField("Порядок", default=0)

    image = models.ImageField("Изображение", upload_to=upload_to)
    image_field_name = "image"
    max_width = 1280
    max_height = 1280
    quality = 75

    class Meta:
        verbose_name = "Изображение экскурсии"
        verbose_name_plural = "Изображения экскурсии"
        ordering = ("sort_order", "id")

    def __str__(self):
        return f"{self.excursion} — #{self.pk}"


class Review(models.Model):
    photo = models.ImageField("Фото", upload_to=upload_to, blank=True, null=True)  # noqa
    full_name = models.CharField("Полное имя", max_length=150)
    text = models.TextField("Текст")
    is_published = models.BooleanField("Опубликовано", default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ("-created_at",)

    def __str__(self):
        return self.full_name


class FAQ(models.Model):
    question = models.CharField("Вопрос", max_length=255)
    answer = models.TextField("Ответ")
    sort_order = models.PositiveIntegerField("Порядок", default=0)
    is_published = models.BooleanField("Опубликовано", default=True)

    class Meta:
        verbose_name = "Часто задаваемый вопрос"
        verbose_name_plural = "Часто задаваемые вопросы"
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.question


class SocialLink(models.Model):
    url = models.URLField("Ссылка")
    fa_icon = models.CharField("Иконка FA (класс)", max_length=64, help_text="Напр.: fa-brands fa-instagram")  # noqa
    title = models.CharField("Название", max_length=50, blank=True, help_text="Опционально, для подсказки")  # noqa
    sort_order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "Соцсеть"
        verbose_name_plural = "Соцсети"
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.title or self.url


class Partner(models.Model):
    name = models.CharField("Название", max_length=150)
    logo = models.ImageField("Логотип", upload_to=upload_to, blank=True, null=True)  # noqa
    url = models.URLField("Сайт", blank=True)
    sort_order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Партнёр"
        verbose_name_plural = "Партнёры"
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.name
