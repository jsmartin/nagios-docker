#! /usr/bin/env python

import pprint

import argparse
import docker
import logging
import nagiosplugin
import subprocess

_log = logging.getLogger('nagiosplugin')


class Docker(nagiosplugin.Resource):

    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout

    def probe(self):
        '''Checks docker stats.

        This method returns the following metrics: 

        `images` is total number of docker images
        on the Docker system. 

        `goroutines` are the number of goroutines.

        `file_descriptors` are the number of open file descriptors.

        `events_listener` are the number of events listener processes.
        '''
        _log.debug('Collect docker info')
        conn = docker.Client(base_url=self.url, timeout=20)
        metrics = []
        try:
            docker_info = conn.info()
            self.docker_running = True
        except:
            self.docker_running = False

        if self.docker_running:
            self.images = docker_info['Images']
            self.go_routines = docker_info['NGoroutines']
            self.file_descriptors = docker_info['NFd']
            self.events_listener = docker_info['NEventsListener']
            metrics = [
                nagiosplugin.Metric('service', self.docker_running, context='null'),
                nagiosplugin.Metric('images', self.images, context='default'),
                nagiosplugin.Metric('go_routines', self.go_routines, context='default'),
                nagiosplugin.Metric('file_descriptors', self.file_descriptors, context='default'),
                nagiosplugin.Metric('events_listener', self.events_listener, context='default') 
                ]

        return metrics

#        return [nagiosplugin.Performance('Number of images', self.images)]


class DockerSummary(nagiosplugin.Summary):

    def verbose(self, results):
    
        super(DockerSummary, self).verbose(results)


def main():

    argp = argparse.ArgumentParser()
    argp.add_argument('-u', '--url', metavar='URL',
                      help='URL string for Docker service.',
                      default='http://127.0.0.1:4243'),
    argp.add_argument('-t', '--timeout', default=10,
                      help='abort execution after TIMEOUT seconds')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)') 

    args = argp.parse_args()



    check = nagiosplugin.Check(Docker(args.url, args.timeout), DockerSummary())
    check.main (args.verbose)




if __name__ == '__main__':
    main()