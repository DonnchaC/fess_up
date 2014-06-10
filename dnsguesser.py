#!/usr/bin/env python

"""Simple DNS guessing script.
nosmo@nosmo.me || https://nosmo.me/~nosmo/

 This script currently checks for A, CNAME and MX records for a
particular domain, doing dumb guessing based on the subdomains in the
subdomain_list list.

This script differs to dnsgrind and subbrute in that it attempts to
get more than simply A or CNAME records. In the long run the plan is
to produce a script that can reproduce a relatively mundane zone file
in a really ham-fisted but complete way.

N(C) license.
"""

import dns.resolver
import dns.rdtypes.ANY.CNAME
import dns.rdtypes.IN.A
import dns.rdtypes.ANY.MX

import collections
import argparse

import pprint

subdomain_list = ["www", "mail",
                  "www2", "dev", None]

dnsobject_map = {
    dns.rdtypes.ANY.CNAME.CNAME: ["target"],
    dns.rdtypes.IN.A.A: ["address"],
    dns.rdtypes.ANY.MX.MX: ["exchange", "preference"]
    }

class DomainScan(object):

    def __init__(self, domain, subdomain_list):
        self.domain = domain
        self.subdomain_list = subdomain_list
        self.data = collections.defaultdict(dict)

    def runScan(self):

        if self._checkWildcards():
            sys.stderr.write(("Wildcard test returned positive - our results "
                              "will be tainted..."))

        for subdomain, record in self._scan("A").iteritems():
            self.data[subdomain]["A"] = record

        for subdomain in self.data.keys():
            for subdomain, records in self._scan("CNAME").iteritems():
                self.data[subdomain]["CNAME"] = [ str(record) for record in records ]

        mxlist = []
        for subdomain in self.data.keys():
            for subdomain, records in self._scan("MX").iteritems():
                for i in xrange(0, len(records), 2):
                    #l[i:i+n]
                    mxlist.append((str(records[i]), records[i+1]))
        self.data[subdomain]["MX"] = mxlist

    def _scan(self, record_type, subdomains=None):
        results = collections.defaultdict(list)
        if not subdomains:
            subdomains = self.subdomain_list

        for subdomain in subdomains:
            query_str = "%s.%s" % (subdomain, self.domain) if subdomain else hostname
            try:
                answers = dns.resolver.query("%s" % (query_str), record_type)
            except dns.resolver.NXDOMAIN as e:
                continue
            except dns.resolver.NoAnswer:
                continue

            record_results = []
            for data in answers:
                record_valuenames = dnsobject_map[type(data)]
                for record_valuename in record_valuenames:
                    record_results.append(getattr(data, record_valuename))
            results[subdomain] = record_results

        return dict(results)

    def _checkWildcards(self):
        try:
            answers = dns.resolver.query("trollllloolololoololo1337lolololololollol.%s" % self.domain)
        except dns.resolver.NXDOMAIN as e:
            return False
        except dns.resolver.NoAnswer:
            return False
        return True

def main(domain):
    domain_scanner = DomainScan(domain, subdomain_list)
    domain_scanner.runScan()
    pprint.pprint(dict(domain_scanner.data))

if __name__ == "__main__":
    hostname = "google.com"
    main(hostname)
