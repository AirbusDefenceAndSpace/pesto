import typer
import time
import json
from pesto.common.testing.service_manager import ServiceManager
from pesto.common.testing.endpoint_manager import EndpointManager
from pesto.ws.service.process import ProcessService
from pesto.cli.core.utils import PESTO_LOG
from pesto.ws.service.job_result import JobResultService, ResultType

app = typer.Typer()

@app.command()
def local(payload: str, output_path: str):
    """
    (Experimental) Run a pesto algorithm locally (not in docker).
    """
    with open(payload) as f:
        content = json.load(f)
        ProcessService.init()
        output, data_type = ProcessService('local').process(content)
        _export_output(output, data_type, output_path)

@app.command()
def docker(payload: str,
           docker_image: str,
           ouptut_path: str,
           host_volume_path: str=typer.Option(None,help="Volume to be mounted from host"),
           image_volume_path: str=typer.Option(None, help="Where the volume is mounted in image"),
           nvidia: bool=typer.Option(False,help="use nvidia runtime"),
           network: str=typer.Option("host",help="Network driver to be used"),
           web_service: bool=typer.Option(True, help="Run the docker in WS mode, true by default. Otherwise processing is exec in container after start")):
    """
    (Experimental) Run a pesto algorithm in a docker. Work only for stateless services
    """
    with ServiceManager(
        docker_image=docker_image,
        host_volume_path=host_volume_path,
        image_volume_path=image_volume_path,
        nvidia=nvidia,
        network=network) as service:
    
        # force restarting service
        if service._existing_container:
            PESTO_LOG.debug("Force restarting service to ensure resources properly mounted")
            service.stop()
            time.sleep(10)
            service.run()
            time.sleep(5)
            
        endpoint_manager = EndpointManager(server_url=service.server_url)
        if not endpoint_manager.describe['asynchronous']:
            if(web_service):            
                with open(payload) as f:
                    with open(ouptut_path,"w") as fout:
                        json.dump(endpoint_manager.process(json.load(f)),fout)
            else:
                PESTO_LOG.info(service._docker_container.exec_run("pesto run local {} {}".format(payload,ouptut_path)).output)
        else:
            raise ValueError('pesto run does not work with stateful services')
        
def _export_output(output: any, data_type: ResultType, output_path: str):        
    if data_type == ResultType.json:
        with open(output_path,'w') as fout:
            json.dump(output,fout)
    elif data_type == ResultType.file:
        with open(output_path,'w') as fout:
            fout.write(output)
    elif data_type == ResultType.image:
        with open(output, "rb") as f:
            image = f.read()
            with open(output_path,'wb') as fout:
                fout.write(image)