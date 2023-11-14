from django.db import models


# Заглушка для модели User, пока она не готова
class User(models.Model):
    username = models.CharField(max_length=100)


# Предварительная модель Review с использованием заглушки User
class Review(models.Model):
    # Пока нет модели User, используем целочисленное поле для id пользователя
    user_id = models.IntegerField()  # Заглушка для ForeignKey на модель User
    text = models.TextField()
    score = models.IntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)


# Для модели комментариев также используем заглушку User
class Comment(models.Model):
    # Аналогично модели Review, используем целочисленное поле для user_id
    user_id = models.IntegerField()  # Заглушка для ForeignKey на модель User
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)


# Заглушка для модели произведения
class Work(models.Model):
    title = models.CharField(max_length=100)
    year = models.IntegerField()

    @property
    def rating(self):
        # Здесь будет логика расчёта рейтинга на основе отзывов
        # Пока что возвращаем заглушку
        return 0  # Заглушка для рейтинга
