# Battlesnake 2018: PirateSnake
#
# CREATORS: - Cameron Day
#			- Carl Marais
#
# PURPOSES: - Be snake.
#			- Survive.
#			- Kill other snakes.
#			- Be the very best - the best there ever was.
#

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
		'head_url': head_url,
		"taunt": "Slither me timbers!",
		'head_type': 'tongue',
		'tail_type': 'curled'
	}


@bottle.post('/move')
def move():
	data = bottle.request.json

	ourSnake = data['you']
	ourHead = ourSnake['body']['data'][0]
	ourTail = ourSnake['body']['data'][-1]
	
	otherSnakes = []

	for snake in data['snakes']['data']:
		otherSnakes.append(snake)
	
	
	foodList = data['food']['data']

	# Eliminate dangerous moves.
	directions = ['up', 'down', 'left', 'right']
	directions = checkWall(data, directions, ourHead)
	print "Directions after checkWall: " + str(directions)
	directions = checkSelf(data, directions, ourHead['x'], ourHead['y'], ourSnake)
	print "Directions after checkSelf: " + str(directions)
	directions = tailAvoidance(data, directions, otherSnakes, ourHead, ourTail)
	print "Directions after tailAvoidance: " + str(directions)
	directions = checkHeadCollision(data, directions, ourHead, ourSnake, otherSnakes)
	print "Directions after checkHeadCollision: " + str(directions)

	# If snake's health is below designated threshold, seek food. Else, pick random direction.

	snake_lengths = [snake['length'] for snake in otherSnakes]

	if ourSnake['health'] <= 2*(data['width'] + data['height']) or ourSnake['length'] <= min(snake_lengths):
		direction = findFood(data, directions, ourHead, foodList)
	else:
		direction = random.choice(directions)

	# For debugging purposes.
	print direction

	# Taunt other slithery, naughty snakes.
	taunts = ['YARRR!', 'Slither me timbers!', 'Ahoy matey!']

	return {
		'move': direction,
		'taunt': random.choice(taunts),
	}

def checkWall(data, directions, ourHead):
	# Remove directions that result in snake running into walls.

	head_x = ourHead['x']
	head_y = ourHead['y']

	# X Directions
	if 'right' in directions and head_x == (data['width'] - 1):
		directions.remove('right')
	elif 'left' in directions and head_x == 0:
		directions.remove('left')
	
	# Y Directions
	if 'down' in directions and head_y == (data['height'] - 1):
		directions.remove('down')
	elif 'up' in directions and head_y == 0:
		directions.remove('up')

	return directions

def checkSelf(data, directions, our_head_x, our_head_y, ourSnake):
	# Remove directions that result in snake running into self.

	head_x = our_head_x
	head_y = our_head_y

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

def findFood(data, directions, ourHead, foodList):
	# Remove directions that result in snake taking longer to reach nearest food.
	# Consider |head_x - food_x| + |head_y - food_y|

	min_dist = 10000 #or height...tbd

	head_x = ourHead['x']
	head_y = ourHead['y']

	for i in range(len(foodList)):
		
		food_i_x = foodList[i]['x']
		food_i_y = foodList[i]['y']

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

def tailAvoidance(data, directions, otherSnakes, ourHead, ourTail):
	# Avoid collisions with other snake bodies.

	head_x = ourHead['x']
	head_y = ourHead['y']

	for snake in otherSnakes:
		if snake['health'] == 0:
			continue
		else:
			for i in range(1, snake['length']):
				snake_i_x = snake['body']['data'][i]['x']
				snake_i_y = snake['body']['data'][i]['y']

				if 'down' in directions:
					if snake_i_x == head_x and snake_i_y == head_y + 1:
						directions.remove('down')
				if 'up' in directions:
					if snake_i_x == head_x and snake_i_y == head_y - 1:
						directions.remove('up')
				if 'right' in directions:
					if snake_i_y == head_y and snake_i_x == head_x + 1:
						directions.remove('right')
				if 'left' in directions:
					if snake_i_y == head_y and snake_i_x == head_x - 1:
						directions.remove('left')

	return directions

def checkHeadCollision(data, directions, ourHead, ourSnake, otherSnakes):
	# Avoid a head to head collision if we are <= the other snake's size

	if len(directions) == 1:
		return directions

	our_head_x = ourHead['x']
	our_head_y = ourHead['y']

	counts = {
		'up': 0,
		'down': 0,
		'left': 0,
		'right': 0,
	}

	for snake in otherSnakes:

		if snake['health'] == 0:
			continue

		snake_head_x = snake['body']['data'][0]['x']
		snake_head_y = snake['body']['data'][0]['y']

		# Up Direction
		if 'up' in directions:
			if our_head_x == snake_head_x and (our_head_y - snake_head_y == 1):
				directions.remove('up')
			elif our_head_x == snake_head_x and (our_head_y - snake_head_y == 2):
				counts['up'] += 1
		# Down Direction
		if 'down' in directions:
			if our_head_x == snake_head_x and (our_head_y - snake_head_y == -1):
				directions.remove('down')
			elif our_head_x == snake_head_x and (our_head_y - snake_head_y == -2):
				counts['down'] += 1
		# Left Direction
		if 'left' in directions:
			if our_head_y == snake_head_y and (our_head_x - snake_head_x == 1):
				directions.remove('left')
			elif our_head_y == snake_head_y and (our_head_x - snake_head_x == 2):
				counts['left'] += 1
		# Right Direction
		if 'right' in directions:
			if our_head_y == snake_head_y and (our_head_x - snake_head_x == -1):
				directions.remove('right')
			elif our_head_y == snake_head_y and (our_head_x - snake_head_x == -2):
				counts['right'] += 1

		if ourSnake['length'] > snake['length']:
			continue

		# Up/Right Direction
		if 'right' in directions or 'up' in directions:
			if (our_head_x - snake_head_x == -1) and (our_head_y - snake_head_y == 1):
				counts['up'] += 1
				counts['right'] += 1
		# Up/Left Direction
		if 'left' in directions or 'up' in directions:
			if (our_head_x - snake_head_x == 1) and (our_head_y - snake_head_y == 1):
				counts['up'] += 1
				counts['left'] += 1
		# Down/Right Direction
		if 'right' in directions or 'down' in directions:
			if (our_head_x - snake_head_x == -1) and (our_head_y - snake_head_y == -1):
				counts['down'] += 1
				counts['right'] += 1
		# Down/Left Direction
		if 'left' in directions or 'down' in directions:
			if (our_head_x - snake_head_x == 1) and (our_head_y - snake_head_y == -1):
				counts['down'] += 1
				counts['left'] += 1

		remove_dir = max(counts, key=counts.get)
		if remove_dir in directions and counts[remove_dir] > 0:
			directions.remove(remove_dir)

		if len(directions) >= 2:
			counts[remove_dir] = 0
			remove_dir = max(counts, key=counts.get)
			if remove_dir in directions and counts[remove_dir] > 0:
				directions.remove(remove_dir)			

	return directions
	#return (directions, min(counts, key=counts.get))

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
	bottle.run(
		application,
		host=os.getenv('IP', '0.0.0.0'),
		port=os.getenv('PORT', '8080'),
		debug = True)
