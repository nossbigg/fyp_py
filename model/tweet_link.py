class TweetLink:
    id = None
    childs = []
    represented_by_id = None

    def __init__(self, id, represented_by_id=None):
        self.id = id
        self.represented_by_id = represented_by_id
