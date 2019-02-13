class index():
  pass

  # Watch directories and index

  def __init__(self):
    self.graphene_mapping = {
      'keyword': graphene.String,
      'text': graphene.String,
      'short': graphene.Int,
      'integer': graphene.Int,
      'float': graphene.Float,
      'boolean': graphene.Boolean
    }
