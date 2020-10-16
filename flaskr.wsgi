activate_this = '"/data/lily/az338/meeting_summ/meeting_ann_interface/meeting/bin/activate"' 

with open(activate_this) as file_:
  exec(file_.read(), dict(__file__=activate_this))


from flaskr import create_app

application = create_app()
