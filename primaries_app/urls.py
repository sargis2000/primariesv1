from django.urls import path
from . views import *
urlpatterns = [
    path('choice_list/', MarkCandidateAPIView.as_view(), name='choice_list'),
    path('evaluate/', EvaluateAPIView.as_view(), name='evaluate'),
    path('news/', NewsAPIView.as_view(), name='news'),
    path('candidate-profiles/', GetCandidateProfiles.as_view(), name='candidate_profiles'),
    path('candidate-profile/', GetCandidateByID.as_view(), name='get_candidate')
]