
m flask.cli import FlaskGroup

from project import app


cli = FlaskGroup(app)


if __name__ == '__main__':
        cli()

@cli.command()
def test():
        """Runs the tests without code coverage"""
            tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
                result = unittest.TextTestRunner(verbosity=2).run(tests)
                    if result.wasSuccessful():
                                return 0
                                return 1

