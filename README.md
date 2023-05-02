# Universal Web Forwarding, via DNS

This server provides a unversal HTTP forwarding service based on the `URI` DNS Recource Record.

As this RR seems to have been otherwise unsed to date (2023-05-02), many DNS maintenance systems do not support
the ability to for users to specify `URI` RR types. For this reason this server will fall back to looking for `TXT` records
which have almost universal support.

## Setting up UWF on your domain

If you have an otherwise unused domain, do the following

- Set your domain to point to one or more UWF nodes (public servers running this software)

For example, if there is a public UWF node running at `10.11.12.13` (there won't be!), add the following
records to your domain

	@ IN A 10.11.12.13
	* IN A 10.11.12.13

- Now all `HTTP` requests for all hostname in your domain will go to the UWF node, so all you need
to do now is start adding UWF records wherever you want them.

For example, if your twitter account is `https://twitter.com/JohnDeo`, then add the record

	_http._tcp.twt IN URL 1 1 "https://twitter.com/JohnDeo"

If your DNS provider does not support `URL` record types, use a `TXT` record instead

	_http._tcp.twt IN TXT "https://twitter.com/JohnDeo"

To set a UWF for the domain itself, set the following

	_http._tcp IN URL 1 1 "https://www.our-web-site.com/"

or

	_http._tcp IN TXT "https://www.our-web-site.com/"

If these were set on the domain `example.com`, then the following web forewarding would work

	http://example.com/ -> https://www.our-web-site.com/
	http://twt.exmaple.com/ -> https://twitter.com/JohnDeo

If you only want to use UWF for certain names, you can chooses to point only those names to the UWF node(s).

For exmaple

	twt IN A 10.11.12.13

With only this address record, instead of the pair above, UWF would only be active on the name `twt`.

For fail-over / load-balancing, you can point to multiple UWF nodes by specifying multiple IP Addresses

For example

	@ IN A 10.11.12.13
	@ IN A 10.11.12.23
	* IN A 10.11.12.13
	* IN A 10.11.12.23

or

	twt IN A 10.11.12.13
	twt IN A 10.11.12.23

NOTE: becuase you can't have different addresses for different protocols, this means the name `twt` can **only** be
used for UWF.


## Suggestions for Different TLAs for different sites

If everybody uses the same three letter prefix for each well known service providers, e.g. `twt` for Twitter, this can become a universal way to find
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

