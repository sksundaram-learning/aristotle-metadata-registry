from haystack import indexes

from aristotle_mdr.search_indexes import conceptIndex

from extension_test import models

class QuestionIndex(conceptIndex, indexes.Indexable):
    def get_model(self):
        return models.Question