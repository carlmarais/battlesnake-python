import bottle
import os
import random



@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data.get('game_id')
    board_width = data.get('width')
    board_height = data.get('height')

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    head_url = 'https://nerdist.com/wp-content/uploads/2015/12/Nicolas-Cage-Con-Air.jpg'

    # TODO: Do things with data

    return {
        'color': 'FFFFFF',
        # 'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'battlesnake-python',
        "taunt": "OH GOD NOT THE BEES",
        'name': 'TROUSER SNAKEBOI',
        'head_type': 'pixel',
        'tail_type': 'pixel'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    # TODO: Do things with data
    
    directions = ['up', 'down', 'left', 'right']
    direction = random.choice(directions)
    print direction
    return {
        'move': direction,
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)
