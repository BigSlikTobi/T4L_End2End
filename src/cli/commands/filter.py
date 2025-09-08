import click

from ...services.llm_classifier import LLMClassifier
from ...services.relevance_filter import RelevanceFilter


# CLI command to filter an article based on title and URL
@click.command(name="filter")
@click.option("--title", required=True)
@click.option("--url", required=True)
@click.option("--use-llm", is_flag=True, default=False)
def filter_cmd(title: str, url: str, use_llm: bool) -> None:
    rf = RelevanceFilter()
    decision, score = rf.filter_article({"title": title, "url": url})
    llm_info = {}
    if use_llm:
        llm = LLMClassifier()
        llm_info = llm.classify_title_url(title, url)
    click.echo({"decision": decision.value, "score": score, "llm": llm_info})


__all__ = ["filter_cmd"]
