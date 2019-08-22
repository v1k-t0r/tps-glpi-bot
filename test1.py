from integrate import TestCase, test
import ses
#target = __import__("ses")
#get_sessions = target.get_sessions
#sessions = target.sessions

class Test(TestCase):
    "get sessions test case"

    @test()
    def get_sessions_test(self, check):
        """test session request"""
        a = ses.get_sessions()
        check.is_not_none(a, message=None)
