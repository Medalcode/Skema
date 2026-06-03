from mangum import Mangum

from skema.api.main import app

handler = Mangum(app)
