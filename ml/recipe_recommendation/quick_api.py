"""Local testing API for the experimental recipe ranker; no additional web package."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
from quick_train import load_model, recommend


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--host',default='0.0.0.0')
    parser.add_argument('--port',type=int,default=8001)
    args=parser.parse_args()
    load_model(args.model)
    class Handler(BaseHTTPRequestHandler):
        def reply(self,status,data):
            body=json.dumps(data).encode()
            self.send_response(status)
            self.send_header('Content-Type','application/json')
            self.send_header('Access-Control-Allow-Origin','*')
            self.send_header('Access-Control-Allow-Headers','Content-Type')
            self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS')
            self.send_header('Content-Length',str(len(body)))
            self.end_headers();self.wfile.write(body)
        def do_OPTIONS(self):
            self.reply(200,{})
        def do_GET(self):
            self.reply(200,{'status':'ready','mode':'experimental_automatic_labels'}) if self.path=='/health' else self.reply(404,{'error':'Not found'})
        def do_POST(self):
            if self.path!='/recommendations':
                self.reply(404,{'error':'Not found'});return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=65536:raise ValueError('Invalid body size')
                data=json.loads(self.rfile.read(length))
                values=data.get('available');limit=data.get('limit',5)
                excluded=data.get('excluded',[])
                if not isinstance(values,list) or any(not isinstance(x,str) for x in values):raise ValueError('available must be a list of ingredient names')
                if not isinstance(excluded,list) or any(not isinstance(x,str) for x in excluded):raise ValueError('excluded must be a list of ingredient names')
                if isinstance(limit,bool) or not isinstance(limit,int) or not 1<=limit<=20:raise ValueError('limit must be1 to20')
                self.reply(200,{'recommendations':recommend(args.model,values,limit,excluded)})
            except (ValueError,TypeError,AttributeError) as error:
                self.reply(400,{'error':str(error)})
            except Exception:
                self.reply(500,{'error':'Recommendation failed; check server terminal'})
                raise
    print(f'Local testing API on port {args.port}; GET /health, POST /recommendations')
    HTTPServer((args.host,args.port),Handler).serve_forever()


if __name__=='__main__':main()
