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
    directions = checkWall(data, directions)
    directions = checkSelf(data, directions)

    direction = random.choice(directions)
    print direction
    return {
        'move': direction,
        'taunt': 'battlesnake-python!'
    }

def checkWall(data, directions):
	# Remove directions that result in snake running into walls

	snake_x = data['you']['body']['data'][0]['x']
	snake_y = data['you']['body']['data'][0]['y']
	# print snake_x, snake_y

	# X Directions
	if snake_x == (data['width'] - 1):
		directions.remove('right')
	elif snake_x == 0:
		directions.remove('left')
	
	# Y Directions
	if snake_y == (data['height'] - 1):
		directions.remove('down')
	elif snake_y == 0:
		directions.remove('up')

	return directions

def checkSelf(data, directions):
	# Remove directions that result in snake running into walls

	snake_x = data['you']['body']['data'][0]['x']
	snake_y = data['you']['body']['data'][0]['y']

	for i in range(len(data['you']['body']['data'])):
		test_x = data['you']['body']['data'][i]['x']
		test_y = data['you']['body']['data'][i]['y']

		if snake_x + 1 == test_x and snake_y == test_y:
			directions.remove('right')
		elif snake_x - 1 == test_x and snake_y == test_y:
			directions.remove('left')
		elif snake_y + 1 == test_y and snake_x == test_x:
			directions.remove('down')
		elif snake_y - 1 == test_y and snake_x == test_x:
			directions.remove('up')

	return directions


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)
