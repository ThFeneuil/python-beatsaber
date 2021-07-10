import datetime

class Score:
    """ A BeatSaber Score.

    :param score: the score value
    :type score: integer
    :param player: the player which obtained this score 
    :type player: string
    :param fullCombo: did the player do a full combo ? By default, False.
    :type fullCombo: boolean
    :param timestamp: the timestamp when the player obtained this score, optional
    :type timestamp: integer
    """
    def __init__(self, score, player, fullCombo=False, timestamp=None):
        # Some checking
        assert type(score) is int
        assert type(player) is str and len(player) <= 15
        assert type(fullCombo) is bool
        assert type(timestamp) is int or (timestamp is None)

        self._score = score
        self._playerName = player
        self._fullCombo = fullCombo
        self._timestamp = timestamp or self.get_current_timestamp()
    
    @classmethod
    def get_current_timestamp(cl):
        return int(datetime.datetime.now().timestamp())
    
    ### Getters
    def get_value(self):
        return self._score
        
    def get_player(self):
        return self._playerName
    
    def is_fullCombo(self):
        return self._fullCombo
    
    ### Setters
    def rename_player(self, name):
        self._playerName = name
    
    ### Comparison operators
    def __eq__(self, other):
        return (self._score == other._score) \
            and (self._fullCombo == other._fullCombo) \
            and (self._timestamp == other._timestamp) \
            and (self._playerName == other._playerName)

    def __ne__(self, other):
        return not (self == other)
    
    def __lt__(self, other):
        # Better score => Before
        if (self._score > other._score):
            return True
        elif (self._score < other._score):
            return False

        # Full Combo => Before
        if (self._fullCombo > other._fullCombo):
            return True
        elif (self._fullCombo < other._fullCombo):
            return False

        # Time Before => Before
        if (self._timestamp < other._timestamp):
            return True
        if (self._timestamp > other._timestamp):
            return False

        # Name Before => Before
        return (self._playerName < other._playerName)
        
    def __le__(self, other):
        return (self < other) or (self == other)

    def __gt__(self, other):
        return  not (self <= other)
    
    def __ge__(self, other):
        return not (self < other)
    
    ### Display functions
    def __str__(self):
        return '{}\t{}\t{}'.format(
                self._score,
                self._playerName,
                'FC' if self._fullCombo else '',
            )
    
    ### Misc
    @classmethod
    def from_json(cl, obj):
        """ Return the Score represented by the given JSON structure.
        The JSON structure must be the same than the used one in Beat Saber application.

        :param obj: the JSON structure
        :param obj: dict
        :rtype: a Score instance
        """
        return cl(
            score=obj['_score'],
            player=obj['_playerName'],
            fullCombo=obj['_fullCombo'],
            timestamp=obj['_timestamp'],
        )
        
    def to_json(self):
        """ Convert the Score into a JSON structure.
        The used JSON structure is the same than the used one by the Beat Saber application.
        
        :rtype: dict
        """
        return {
            '_score': self._score,
            '_playerName': self._playerName,
            '_fullCombo': self._fullCombo,
            '_timestamp': self._timestamp,
        }
