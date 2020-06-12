
from django.conf.urls import url
from .views import startNew, copy_example, checkStatus

urlpatterns = [
    # url(r'results', views.result_new, name='srnabench'),
    # #url(r'results', views.result),
    # url(r'table/(.+)/(.+)/(.+)*', views.render_table, name='table_bench'),
    # url(r'align/(.+)/(.+)/(.+)', views.show_align, name='show_align'),
    # # url(r'run$', views.run, name='run_bench'),
    #
    # url(r'test$', views.test),
    url(r'upload/[A-za-z0-9]+', startNew.as_view()),
    url(r'upload', copy_example, name="spike_example"),
    url(r'^check', checkStatus.as_view(), name="spike_status"),
    url(r'example/[A-za-z0-9]+', startNew.as_view()),
    url(r'example/[A-za-z0-9]+', startNew.as_view()),
    url(r'^$', startNew.as_view()),
]
