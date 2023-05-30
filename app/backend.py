import json
import argparse
import logging 
from typing import Optional, Dict
import time 

from flask import Flask, jsonify, request
from haystack import Pipeline

from config import APP_PIPELINE_CONFIG_PATH
from src.inference_hs.final_evidence_fusion import FinalEvidenceFusionNode

_log = logging.getLogger(__name__)
_log.setLevel(logging.INFO)


def _parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run ORQA backend app.",
    )
    # overwrite default config pipeline file
    parser.add_argument(
        "--pipeline_config_path",
        nargs="?",
        default=APP_PIPELINE_CONFIG_PATH / 'basic.haystack-pipeline.yml',
        help=f"Pipeline config for this backend, defaults to "
              "`app/config/basic.haystack-pipeline.yml`.",
    )
    parser.add_argument(
        "--pipeline_name",
        nargs="?",
        default='query_pipeline',
        help="Name of pipeline to run in the pipeline config. Defaults to `query_pipeline`",
    )
    parser.add_argument(
        "--doc_index",
        nargs="?",
        default='natural_questions_docs',
        help="Name of document index in document store",
    )
    parser.add_argument(
        "--label_index",
        nargs="?",
        default='natural_questions_labels',
        help="Name of label index in document store",
    )
    parser.add_argument(
        "--port",
        nargs="?",
        default=5000,
        help="Port to run this app on.",
    )
    return parser.parse_args()


def _initialize_pipeline(args: argparse.Namespace) -> Pipeline:
    """Initialize a pipeline using config."""
    _log.info(f'Loading pipeline {args.pipeline_name} from `{args.pipeline_config_path}`')
    pipeline = Pipeline.load_from_yaml(
        args.pipeline_config_path,
        pipeline_name=args.pipeline_name,
    )
    _log.info('Successfully loaded pipeline!')
    
    ds = pipeline.get_document_store()
    _log.info(f'Document store contains {ds.get_document_count(index=args.doc_index)} '
              f'documents and {ds.get_label_count(index=args.label_index)} labels')
    
    return pipeline


def _create_app():
    app = Flask(__name__)

    app.config.update(dict(DEBUG=False))

    @app.route('/query', methods=['POST'])
    def predict() -> Optional[Dict]:
        if request.method == 'POST':
            data = json.loads(request.get_data())
            
            start = time.perf_counter()
            
            #pipeline = PIPELINE.get(data['pipeline_type'])
            #if pipeline is None:
            #    return jsonify({})
            
            model_output = pipeline.run(data['query'])
            runtime = time.perf_counter() - start
            
            answers = [answer.to_dict() for answer in model_output['answers']]
            documents = [document.to_dict() for document in model_output['documents']]
            
            _log.info(f'answers: {answers}')
            
            response = {
                'answers': answers,
                'documents': documents,
                'runtime': runtime,
            }

            _log.info(response)
        
            return jsonify(response)
        
        else:
            return jsonify({})
        
    @app.route('/docstorestats', methods=['GET'])
    def get_docstore_stats() -> Optional[Dict]:
        if request.method == 'GET':
            ds = pipeline.get_document_store()
            
            response = {
                'document_count': ds.get_document_count(index=args.doc_index),
            }

            return jsonify(response)
        
        else:
            return jsonify({})

    return app


if __name__ == '__main__':
    args = _parse_args()
    pipeline = _initialize_pipeline(args)
    
    app = _create_app()
    app.run(port=args.port)
    