class TweetLink:
    id = None
    childs = []
    represented_by_id = None

    def __init__(self, id, represented_by_id=None):
        self.id = id
        self.represented_by_id = represented_by_id
        self.childs = []

    def to_mongo_item(self):
        return {
            "_id": self.id,
            "childs": self.childs,
            "represented_by_id": self.represented_by_id
        }
