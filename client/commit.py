from datetime import datetime
class Commit:

    def __init__(self,message):
        self.hash_code=hash(self)
        self.date_time=datetime.now()
        self.message=message
