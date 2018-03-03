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

	head_url = 'http://cheesepirate.com/avatars/nate_the_pirate_snake.png'

	return {
		'color': '#FFB600',
		# 'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
		'head_url': head_url,
		"taunt": "Slither me timbers",
		'head_type': 'tongue',
		'tail_type': 'curled'
	}


@bottle.post('/move')
def move():
	data = bottle.request.json


	# TODO: Do things with data

	ourSnake = data['you']
	ourHead = ourSnake['body']['data'][0]
	otherSnakes = []

	for snake in data['snakes']:
		otherSnakes.append(snake)
	
	directions = ['up', 'down', 'left', 'right']
	directions = checkWall(data, directions, ourHead)
	directions = checkSelf(data, directions, ourHead, ourSnake)

	if data['you']['health'] <= 50:
		direction = findFood(data, directions)
	else:
		direction = random.choice(directions)

	print direction

	taunts = {'test', 'test2', 'test3', 'test4'}

	return {
		'move': direction,
		'taunt': random.choice(taunts),
	}

def checkWall(data, directions, ourHead):
	# Remove directions that result in snake running into walls

	snake_x = ourHead['x']
	snake_y = ourHead['y']

	# X Directions
	if 'right' in directions and snake_x == (data['width'] - 1):
		directions.remove('right')
	elif 'left' in directions and snake_x == 0:
		directions.remove('left')
	
	# Y Directions
	if 'down' in directions and snake_y == (data['height'] - 1):
		directions.remove('down')
	elif 'up' in directions and snake_y == 0:
		directions.remove('up')

	return directions

def checkSelf(data, directions, ourHead, ourSnake):
	# Remove directions that result in snake running into walls

	head_x = ourHead['x']
	head_y = ourHead['y']

	for i in range(len(data['you']['body']['data'])):
		body_x = ourSnake['body']['data'][i]['x']
		body_y = ourSnake['body']['data'][i]['y']

		if 'right' in directions and head_x + 1 == body_x and head_y == body_y:
			directions.remove('right')
		elif 'left' in directions and head_x - 1 == body_x and head_y == body_y:
			directions.remove('left')
		elif 'down' in directions and head_y + 1 == body_y and head_x == body_x:
			directions.remove('down')
		elif 'up' in directions and head_y - 1 == body_y and head_x == body_x:
			directions.remove('up')

	return directions

def findFood(data, directions):
	#Select nearest food. Eliminate directions that would take longer to reach that food.
	#|head_x - food_x| + |head_y - food_y|

	min_dist = data['width'] #or height...tbd

	head_x = data['you']['body']['data'][0]['x']
	head_y = data['you']['body']['data'][0]['y']

	for i in range(len(data['food']['data'])):
		
		food_i_x = data['food']['data'][i]['x']
		food_i_y = data['food']['data'][i]['y']

		dist_food_i = abs(head_x - food_i_x) + abs(head_y - food_i_y)

		if dist_food_i <= min_dist:

			min_dist = dist_food_i

			closest_food = i
			closest_food_x = food_i_x
			closest_food_y = food_i_y

	choices = {key: None for key in directions}

	if 'left' in directions:
		choices['left'] = abs(head_x - closest_food_x - 1) + abs(head_y - closest_food_y)
	if 'right' in directions:
		choices['right'] = abs(head_x - closest_food_x + 1) + abs(head_y - closest_food_y)
	if 'up' in directions:
		choices['up'] = abs(head_x - closest_food_x - 1) + abs(head_y - closest_food_y - 1)
	if 'down' in directions:
		choices['down'] = abs(head_x - closest_food_x - 1) + abs(head_y - closest_food_y + 1)

	return min(choices, key=choices.get)

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
	bottle.run(
		application,
		host=os.getenv('IP', '0.0.0.0'),
		port=os.getenv('PORT', '8080'),
		debug = True)
