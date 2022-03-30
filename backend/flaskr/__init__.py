import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_question(request,selection):
  page=request.args.get('page',1, type=int)
  start=(page-1)*QUESTIONS_PER_PAGE
  end=start+QUESTIONS_PER_PAGE
  questions=[question.format() for question in selection]
  current_question=questions[start:end]

  return current_question


def search_questions(data):
  search_term=data
  related_questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
    
  if related_questions==[]:
    abort(404)

  output = paginate_question(request, related_questions)

  return jsonify({
    'succes': True,
    'questions': output,
    'totalQuestions': len(related_questions),
      
  })    


def create_app(test_config=None):
  
  app = Flask(__name__)
  setup_db(app)
  #|----------------------|
  #|         CORS         |
  #|----------------------|  
  
  CORS(app, resources={"/": {"origins": "*"}})


  @app.after_request
  def after_request(response):
    response.headers.add(
      "Access-Control-Allow-Headers","Content-Type,Authorization,true"

      )
    response.headers.add(
      "Access-Control-Allow-Methods","GET,PUT,POST,DELETE,OPTIONS"


      )

    return response

  #|----------------------|
  #|       MAIN PART      |
  #|----------------------|    


  @app.route('/categories') 
  def categories():
    categories=Category.query.all()

    get_categories={}
    for category in categories:
      get_categories[category.id]=category.type

    if len(categories)==0:
      abort(404)

    return jsonify({
      'succes':True,
      'categories':get_categories
      })  



  @app.route('/questions', methods=['GET'])
  def get_question():

    selection=Question.query.all()
    len_question=len(selection)
    current_question=paginate_question(request,selection)


    get_categories={}
    categories=Category.query.all()
    for category in categories:
      get_categories[category.id]=category.type

    if len(current_question)==0:
      abort(404)

    return jsonify({
      'succes':True,
      'questions':current_question,
      'categories':get_categories,
      'totalQuestion':len_question

      })

  @app.route('/categories/<int:id>/questions', methods=['GET'])
  def question_by_category(id):
    category = Category.query.get(id)

    if category is None:
      abort(404)

    category_id=str(category.id)
    questions = Question.query.filter_by(category=category_id).all()
    current_questions = paginate_question(request, questions)
    
    return jsonify({
      'succes': True,
      'questions': current_questions,
      'currentCategory': category.type,
      'totalQuestions': len(questions)
      })



  @app.route('/questions/<int:id>',methods=['DELETE'])
  def delete_question(id):
    try:
      delete_question = Question.query.get(id)
      if delete_question is None:
        abort(404)
      delete_question.delete()
      return jsonify({
        'succes':True,
        'delete':id

        })
    except:
      abort(422)
      
      
  @app.route('/quizzes', methods=['POST'])
  def quiz_question():

    body = request.get_json()
 

    category = body['quiz_category']
    previous_questions = body['previous_questions']
    if category['id'] != 0:
      questions = Question.query.filter_by(category=category['id']).all()
    
    else:
      questions = Question.query.all()

    if len(questions)==0:
      abort(500)

      

    def get_random_question():
      next_question = random.choice(questions).format()
      return next_question

    next_question = get_random_question()

     
    return jsonify({
    'succes': True,
    'question': next_question
    })





  @app.route('/questions',methods=['POST'])
  def new_question():
    body=request.get_json()
    try:
      #question search
      search_item=body['searchTerm']
      return search_questions(search_item)
    except: 
      #create question
      question=body['question'],
      answer=body['answer'],
      difficulty=body['difficulty'],
      category=body['category']
      
      if (len(question)==0) or (len(answer)==0):
        abort(422)
      new_quest=Question(
        question=question,
        answer=answer,
        difficulty=difficulty,
        category=category
        )

      new_quest.insert()
      all_question=Question.query.all()
      current_question=paginate_question(request,all_question)
      return jsonify({
        'succes':True,
        'created':new_quest.id,
        'questions':current_question,
        'totalQuestion':len(all_question)
        })

  #question search
  @app.route('/questions/search',methods=['POST'])
  def question_search():
    body=request.get_json()
    search_item=body['searchTerm']
    return search_questions(search_item)
  #|----------------------|
  #|    CREATE CATEGORY   |
  #|----------------------|
  @app.route('/categories' ,methods=['POST'])
  def create_category():
    body=request.get_json()
    if len(body['category'])==0:
      abort(422)

    category=body['category']

    new_category=Category(
      type=category
      )
    new_category.insert()
    return jsonify({
      'succes':True,
      'new_category':new_category.type
      })
    @app.route('/example', methods=['GET'])
    def salom():
      data=request.args.get('num',1,type=int)
      
      return jsonify({
        'data':data
        })




  #[-----------------]
  #[      ERROR      ]
  #[-----------------]
  @app.errorhandler(400)
  def bad_request(error):
    return (jsonify({
      'succes':False,
      'error':400,
      'message':'Bad request'
      }),400)

  @app.errorhandler(404)
  def not_found(error):
    return (jsonify({
      'succes':False,
      'error':404,
      'message':"Page not found"
      }),404)

  @app.errorhandler(422)
  def unprocessable(error):
    return (jsonify({
      'succes':False,
      'error':422,
      'message':'Unprocessable. Syntax error.'
      }),422)

  @app.errorhandler(500)
  def server_error(error):
    return (jsonify({
      'succes':False,
      'error':500,
      'message':'Internal server error. Please try again later'
      }),500)

  
  return app

    