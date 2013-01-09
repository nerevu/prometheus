---
heading: About Prometheus
subheading: Learn about the philosophy behind Prometheus and how it was created
---

## What is Prometheus?

### Inspiration

The inspiration for Prometheus came from the lack of adequate tools for managing investment portfolios. Currently available applications lack support for managing investments ([Mint](www.mint.com)), present a conflict of interest through management fees or ties to brokerage firms ([Betterment](http://www.betterment.com/), [Wealthfront](http://www.wealthfront.com/)), or are limited in the number of asset classes they provide exposure to ([MarketRiders](http://www.marketriders.com/), [FutureAdvisor](https://www.futureadvisor.com/)).

### Features

Prometheus aims to give investors an easy way to:

* construct portfolios of low cost ETFs and mutual funds
* generate customized portfolios based on their individual risk tolerance
* access asset classes that have since only been available to the elite

Prometheus provides a suite of tools to:

* track and monitor portfolio performance and allocation
* compare portfolios across various categories (account, manager, etc.)
* visualize various portfolio metrics

### Philosophy

Coupled with the above tenants is commitment to [open source software](http://en.wikipedia.org/wiki/Free_and_open_source_software). There is a large amount of open source [finance and investment code](http://cran.r-project.org/web/views/Finance.html) available which lowers the barrier to creating complex financial applications. Drawing on this existing framework lowers development time and leverages the expertise of the entire finance community. When possible, Prometheus will [give back](http://tom.preston-werner.com/2011/11/22/open-source-everything.html) to the open source community by providing [permissive licenses](http://en.wikipedia.org/wiki/Permissive_free_software_licence) to code base not integral to its core business.

Ultimately, Prometheus will provide a user friendly application with an open platform and developer friendly API. Prometheus will strive to become the [platform of choice](http://www.techdirt.com/blog/entrepreneurs/articles/20110531/01505814470/being-someone-elses-bitch-being-your-own-bitch-making-others-your-bitch.shtml) for developing financial applications.

- - -

## Beyond modern portfolio theory (MPT)

 With the view that investment returns are not normally distributed (especially in the case of [alternative investments](http://www.macroption.com/non-normal-return-distribution-alternative-investments/)) Prometheus embraces the following principles of post-modern portfolio theory (PMPT):

* [Downside deviation](http://en.wikipedia.org/wiki/Downside_risk)
* [Sortino Ratio](http://en.wikipedia.org/wiki/Sortino_ratio)
* [PMPT](http://en.wikipedia.org/wiki/Post-modern_portfolio_theory)
* [Random portfolios](http://www.portfolioprobe.com/)
* [Hedge fund replication](http://en.wikipedia.org/wiki/Hedge_fund_replication)

- - -

## The making of Prometheus

Prometheus is written entirely in [Python](http://python.org/) using [Flask](http://flask.pocoo.org/), [SQLAlchemy](http://sqlalchemy.org/), [Pandas](http://pandas.pydata.org/), [Google Charts](https://developers.google.com/chart/interactive/docs/index)	, and [Bootstrap](http://twitter.github.com/bootstrap/). The API was generated using [Flask-Restless](https://flask-restless.readthedocs.org/). Static pages (e.g., the page you are now reading) were generated using [Flask-Markdown](http://packages.python.org/Flask-Markdown/).