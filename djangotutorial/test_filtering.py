import django.test
from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.auth.models import User

class TestLogEntry(django.test.TestCase):
  def test_log_filtering_2000(self):
    user1 = User.objects.create(username='user1')
    LogEntry.objects.create(user=user1, action_flag=ADDITION, change_message='a' * 2000)
    self.assertEqual(len(LogEntry.objects.only('id').filter(change_message__contains='a')), 1)

  def test_log_filtering_2001(self):
    user1 = User.objects.create(username='user1')
    LogEntry.objects.create(user=user1, action_flag=ADDITION, change_message='a' * 2001)
    self.assertEqual(len(LogEntry.objects.only('id').filter(change_message__contains='a')), 1)