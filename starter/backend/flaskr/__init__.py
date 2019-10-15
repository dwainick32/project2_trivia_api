import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from random import choice, randint

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE, OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    categories = [i.format() for i in categories]
    return jsonify(categories)
  
  @app.route('/categories/<int:category_id>')
  def category(category_id):
    category = Category.query.get(category_id)
    category = category.format()
    if category is None:
      abort(404)
    else:
      return jsonify(category)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10
    questions = Question.query.order_by(Question.id).all()
    categories = Category.query.all()
    categories = [i.format() for i in categories]
    formatted_questions = [question.format() for question in questions]
    return jsonify({
      'success': True,
      'questions': formatted_questions[start:end],
      'total_questions': len(formatted_questions),
      'current_category': 'All',
      'categories': categories
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    Question.query.filter(Question.id == question_id).delete()
    db.session.commit()
    db.session.close()
    return jsonify({
      "success": True,
      'message': "Delete occured"
    })
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions/create', methods=['POST'])
  def create_new_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
    if new_question is None or new_answer is None:
      abort(422) 

    question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
    question.insert()
    new_question = Question.query.get(question.id)
    new_question = new_question.format()

    return jsonify({
      'success': True, 
      'created': question.id,
      'new_question': new_question,
      'total question': len(Question.query.all())
    })




  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    term = body.get('search', None)
    search = Question.query.filter(Question.question.ilike(f'%{term}%')).all()
    search = [s.format() for s in search]  
    return jsonify({
      'success': True,
      'questions': search
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category>/questions')
  def get_category_questions(category):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10
    questions = Question.query.filter(Question.category == category).all()
    if len(questions) == 0:
      abort(404)
    formatted_questions = [question.format() for question in questions]
    return jsonify({
      'success': True,
      'questions': formatted_questions[start:end],
      'total_questions': len(formatted_questions),
      'current_category': category
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/play', methods=['POST'])
  def play():
    body = request.get_json()
    category = body.get('category', None)
    previous_question_ids = body.get('previous_questions', None)
    if category is not None:
      #query database for one questions in category
      questions = Question.query.filter(Question.category == category).all()
      formatted_questions = [q.format() for q in questions]  
      if previous_question_ids:
        random_num = choice([i for i in range(0, len(formatted_questions)-1) if i not in previous_question_ids])
      else:
        random_num = randint(0, len(formatted_questions)-1)
      return jsonify({
        'success': True, 
        'total_questions': len(formatted_questions),
        'current_question': formatted_questions[random_num]
        })
    else:
      questions = Question.query.all()
      formatted_questions = [q.format() for q in questions]
      if previous_question_ids:        
        random_num = choice([i for i in range(0, len(formatted_questions)-1) if i not in previous_question_ids])
      else:
        random_num = randint(0, len(formatted_questions)-1)
      #print(formatted_questions[random_num])
      return jsonify({
        'success': True,
        'total_questions': len(formatted_questions),
        'current_question': formatted_questions[random_num]        
      })

  
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404, 
      "message": "Not Found"
    }), 404
  
  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      "success": False,
      "error": 422, 
      "message": "Unprocessable Entity"
    })

  return app