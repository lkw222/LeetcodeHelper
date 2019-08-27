from django.db import models

# Create your models here.

class Question(models.Model):
    question_slug = models.SlugField(primary_key=True, unique=True)
    front_id = models.IntegerField()
    content = models.TextField()
    name = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=10)
    total_accept = models.IntegerField()
    total_submission = models.IntegerField()
    accept_rate = models.FloatField()
    paid_only = models.BooleanField()
    like = models.IntegerField()
    dislike = models.IntegerField()
    frequency = models.FloatField()

    def __str__(self):
        return self.name


class Company(models.Model):
    company_slug = models.SlugField(primary_key=True, unique=True)
    name = models.CharField(max_length=100)
    hire_link = models.URLField(null=True)

    def __str__(self):
        return self.name


class CompanyTag(models.Model):
    company_slug = models.ForeignKey(Company, on_delete=True)
    question_slug = models.ForeignKey(Question, on_delete=True)
    vote_count = models.IntegerField()

    def __str__(self):
        return self.company_slug.name + ': ' + self.question_slug.name

class Algorithm(models.Model):
    algorithm_slug = models.SlugField(primary_key=True, unique=True)
    name = models.CharField(max_length=100)
    topic_link = models.URLField(null=True)

    def __str__(self):
        return self.name


class AlgorithmTag(models.Model):
    algorithm_slug = models.ForeignKey(Algorithm, on_delete=True)
    question_slug = models.ForeignKey(Question, on_delete=True)

    def __str__(self):
        return self.algorithm_slug.name + ': ' + self.question_slug.name

class Similar(models.Model):
    cur_question_slug = models.ForeignKey(Question, on_delete=True, related_name='%(class)s_requests_created')
    tar_question_slug = models.ForeignKey(Question, on_delete=True)
    tar_difficulty = models.CharField(max_length=10)

    def __str__(self):
        return self.cur_question_slug.name + ' -> ' + self.tar_question_slug.name
