from dataclasses import dataclass

MAX_HEALTH = 10
VICTORY_PTS_WIN = 20
DIE_COUNT = 6


CARD_WIDTH, CARD_HEIGHT = 300, 150
CARD_BORDER_RADIUS = 10
CARD_PADDING = 10


class DIESIDE:
    ATTACK = 'Attack'
    HEAL = 'Heal'
    ONE = '1'
    TWO = '2'
    THREE = '3'


PIXEL_UNICODE = {
    DIESIDE.ATTACK: u'\u2197',
    DIESIDE.HEAL: u'\u2665',
    DIESIDE.ONE: '1',
    DIESIDE.TWO: '2',
    DIESIDE.THREE: '3',
    'VP': u'\u2605',
    'EMPTY': ''
}


@dataclass
class PlayerState:
    health: int = 10
    victory_points: int = 0
    in_tokyo: bool = False
