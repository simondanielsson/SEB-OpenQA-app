# SEB-OpenQA-app

This is a web application for open-domain question-answering (OpenQA) systems. It was built
during the Master's thesis project _Question-answering in the Financial Domain_ (Simon Danielsson & Nils Romanus) at the Faculty of Engineering at Lund University, 
in conjunction with the Swedish bank SEB.

## How to run

Begin by configuring the pipeline in `app/config/basic.haystack-pipeline.yml`.

Then, run the backend by executing the following command with the appropriate flags.

```bash
usage: backend.py [-h] [--pipeline_config_path [PIPELINE_CONFIG_PATH]]
                  [--pipeline_name [PIPELINE_NAME]] [--doc_index [DOC_INDEX]]
                  [--label_index [LABEL_INDEX]] [--port [PORT]]

Run ORQA backend app.

options:
  -h, --help            show this help message and exit
  --pipeline_config_path [PIPELINE_CONFIG_PATH]
                        Pipeline config for this backend, defaults to `app/config/basic.haystack-
                        pipeline.yml`.
  --pipeline_name [PIPELINE_NAME]
                        Name of pipeline to run in the pipeline config. Defaults to `query_pipeline`
  --doc_index [DOC_INDEX]
                        Name of document index in document store
  --label_index [LABEL_INDEX]
                        Name of label index in document store
  --port [PORT]         Port to run this app on.
```

for instance,

```bash
python3 app/backend.py\
  --pipeline_name 'basic_ranker_pipeline'\
  --doc_index "natural_questions_docs"\
  --label_index "natural_questions_labels"
```

Then do requests with a query to the `/query` endpoint. For instance,

```bash
curl -X POST http://<your_ip>/query -d '{"query": <my_query>}'
```

You can also run the streamlit frontend by invoking

```bash
streamlit run app/frontend.py --server.enableCORS=false --server.enableXsrfProtection=false
```

If you want to run it on GCP, create a port mapping by running the following in gcloud shell

```bash
gcloud compute ssh --zone <your_zone> <vm_name> --project <project_name> -- -L 8501:<frontend_ip>:<frontend_port>
```

and visit the app on port 8501.