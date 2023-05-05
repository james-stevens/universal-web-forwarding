# Universal Web Redirect, via DNS

This server provides a unversal HTTP redirection service based on the (`URI` DNS Recource Record)[https://en.wikipedia.org/wiki/URI_record].

As this RR seems to have been otherwise unsed to date (2023-05-02), many DNS maintenance systems do not support
the ability to for users to specify `URI` RR types. For this reason this server will fall back to looking for `TXT` records
which have almost universal support.

## Setting up UWR on your domain

If you have an otherwise unused domain, do the following

- Set your domain to point to one or more UWR nodes (public servers running this software)

For example, if there is a public UWR node running at `10.11.12.13` (there won't be!), add the following
records to your domain

	@ IN A 10.11.12.13
	* IN A 10.11.12.13

- Now all `HTTP` requests for all hostname in your domain will go to the UWR node, so all you need
to do now is start adding UWR records wherever you want them.

For example, if your twitter account is `https://twitter.com/JohnDeoTheThird`, then add the record

	_http._tcp.twt IN URL 1 1 "https://twitter.com/JohnDeoTheThird"

If your DNS provider does not support `URL` record types, use a `TXT` record instead

	_http._tcp.twt IN TXT "https://twitter.com/JohnDeo"

To set a UWR for the domain itself, set the following

	_http._tcp IN URL 1 1 "https://www.our-web-site.com/"

or

	_http._tcp IN TXT "https://www.our-web-site.com/"

If these UWR records were set on the domain `example.com`, then the following web redirections would work

	http://example.com/ -> https://www.our-web-site.com/
	http://twt.exmaple.com/ -> https://twitter.com/JohnDeoTheThird

So, when any usser click the URL `exmaple.com` they will be sent to `https://www.our-web-site.com/`.

If you only want to use UWR for certain names, you can chooses to point only those names to the UWR node(s).

For exmaple

	twt IN A 10.11.12.13

With only this address record, instead of the address pair above, UWR would only be active on the name `twt`.

For fail-over / load-balancing, you can point to multiple UWR nodes by specifying multiple IP Addresses

For example

	@ IN A 10.11.12.13
	@ IN A 10.11.12.23
	* IN A 10.11.12.13
	* IN A 10.11.12.23

or

	twt IN A 10.11.12.13
	twt IN A 10.11.12.23


## NOTES

1. For records of type `URI` the fields `priority` and `weight` are not (yet) implemented.

2. Where only one URL is given an `HTTP 301 Redirect` is given.
Where more than one URL is given one URL is picked at random and an `HTTP 302 Redirect` is given.

3. Becuase you can't have different IP addresses for different protocols, pointing a hostname to a UWR node means that hostname can **only** be used for UWR.
For example, HTTPS will still resolve to the UWR's IP Address, but will not work.

4. UWR does **NOT** support HTTPS, for lots of reasons. In fact UWR **ONLY** supports HTTP, nothing else.

5. UWR **will** support non-ICANN domain naming system, but ONLY if **BOTH** the client and UWR node(s) can resolve the non-ICANN domain names.

6. If a hostname resolves to the IP of a UWR node, but the node can't find an exact match `URI` or `TXT` record for that hostname,
it will then look for a record at the hostname `_any.<domain>`. This is so users can have a default matching URL when using the wild card hostname. (not yet implemented)


## Running your own UWR Node

To run your own UWR node, simple run this container on a public IP Address, port 80.

You can either build this container from its soruce code by running `./dkmk` in this directory, or use the
container `jamesstevens/universal-web-redirect` from `docker.com`.


## Suggestions for Different TLAs for different sites

If everybody uses the same three letter prefix for each well known service provider, e.g. `twt` for Twitter, this could become a universal way to find
somebody's social media account, once you know their personal domain name.

Here's some suggestions

| TLA | Service |
| --- | ------- |
| twt | Twitter |
| fbk | Facebook |
| tkk | TikTok |
| ins | Instagram |
| ytb | YouTube |
| lnk | LinkedIn |
| pin | Pintrest |
| red | Reddit |

