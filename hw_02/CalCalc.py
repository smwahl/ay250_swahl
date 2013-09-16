''' CalCalc.py
Sean Wahl, University of California Berkeley

Calculator module for AY-250 python class
'''

# import packages
import argparse
import urllib2 as ul
import re
from lxml import etree


def calculate(inputStr,force_eval=False,force_wolfram=False):
    '''Evaluates any string passed to it, and can be used from either the command line.
Interacts with the Wolfram|Alpha API what when asked what it thinks is a  'difficult'
question

Examples:

$ python CalCalc.py -s '34*28'
$ 952

$ python CalCalc.py 'mass of the moon in kg'
$  7.3459e+22

'''

    # test for incompatible options
    if force_eval == True and force_wolfram == True:
        print 'Error: force_eval and force_wolfram options incompatible.'
        raise

    if force_wolfram == False:
        try:
            return str(eval(inputStr))
        except:
                print "Exception raised using python's eval().",
                if force_eval == False: print  " Trying wolfram alpha instead." 
                else: print " "

    if force_eval == False:
        # get url for wolfram api
        wolfStr = re.sub('\s+',r'%20',inputStr)
        url_name = ''.join(['http://api.wolframalpha.com/v2/query?input=',wolfStr,'&appid=UAGAWR-3X6Y8W777Q'])
        wolfram_url = ul.urlopen(url_name)

        # Parse xml
        tree = etree.parse(wolfram_url)

        # determine if query was successful
        try:
            query = tree.iter().next()
            queryDict = dict(query.items())
            query_success = bool(queryDict['success'])  
        except:
            print 'Unexpected Error: Problem finding result with Wolfram Alpha api'
            raise

        # find the and return the plaintext result
        if query_success:
            pods = tree.findall('.//pod')
            for pod in pods:
                try:
                    podDict =  dict(pod.items())
                    if podDict['title']=='Result':
                        print 'found result'
                        resultPod = pod
                except:
                    print 'Unexpected Error: Problem finding result with Wolfram Alpha api'
                    raise

            txt = resultPod.find('.//plaintext')
            txt2 = re.findall(r'<plaintext>(.*)</plaintext>', etree.tostring(txt))[0]
            txt3 = re.sub(r'&#215;10\^','e',txt2) # fixes scientific notation
            return txt3
        else:
            print 'No solution found using Wolfram api'
            return None




def test_1():
    assert abs(4. - calculate('2**2')) < .001


# run from the command line
if __name__ == '__main__':
    descriptionText = '''CalCalc.py
Sean Wahl, University of California Berkeley

Calculator module for AY-250 python class.
Evaluates any string passed to it, and can be used from either the command line.
Interacts with the Wolfram|Alpha API what when asked what it thinks is a  'difficult'.
question.'''

    exampleText =  '''Examples:
$ python CalCalc.py -s '34*28'
$ 952

$ python CalCalc.py 'mass of the moon in kg'
$  7.3459e+22''' 

    #define argument parser
    parser = argparse.ArgumentParser(description=descriptionText, epilog = exampleText, 
            formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('string_to_eval1', help='String to be evaluate.')
    parser.add_argument('-s', action='store_true', dest='force_eval',
                        help='Force input to be evaluated with pythons eval()')
    parser.add_argument('-w', action='store_true', dest='force_wolfram',
                        help='Force input to be evaluated with wolfram alpha')
    parser.add_argument('--version', action='version', version='%(prog) 1.0')

    # parse arguments
    args = parser.parse_args()

    # Evaluate string using calculate()
    result = calculate(args.string_to_eval1,force_eval=args.force_eval,force_wolfram=args.force_wolfram)

    # display result
    print result
