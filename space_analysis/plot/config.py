# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/plot/01_plt_config.ipynb.

# %% auto 0
__all__ = ['FigureExtraOptions']

# %% ../../nbs/plot/01_plt_config.ipynb 0
from pydantic import (
    BaseModel,
)

from matplotlib.pyplot import Figure, Axes

# %% ../../nbs/plot/01_plt_config.ipynb 1
class FigureExtraOptions(BaseModel):
    """Options to apply to a matplotlib figure."""

    hide_legends: bool = False
    hide_ylabels: bool = False
    sync_legend_colors: bool = False
    hide_legend_lines: bool = False

    def process(self, fig: Figure, axes: list[Axes]) -> None:
        """Apply extra options to a matplotlib figure and its axes."""

        # Process each option through its dedicated method
        if self.hide_legends:
            self._hide_legends(axes)
        if self.hide_ylabels:
            self._hide_ylabels(axes)
        if self.sync_legend_colors:
            self._sync_legend_colors(axes)
        if self.hide_legend_lines:
            self._hide_legend_lines(axes)

    def _hide_legends(self, axes: list[Axes]) -> None:
        """Hide legends on all axes."""
        for ax in axes:
            legend = ax.get_legend()
            if legend:
                legend.remove()

    def _hide_ylabels(self, axes: list[Axes]) -> None:
        """Hide y-axis labels on all axes."""
        for ax in axes:
            ax.set_ylabel("")

    def _sync_legend_colors(self, axes: list[Axes]) -> None:
        """Synchronize legend text colors with their corresponding line colors."""
        for ax in axes:
            legend = ax.get_legend()
            if legend:
                for line, text in zip(legend.get_lines(), legend.get_texts()):
                    text.set_color(line.get_color())

    def _hide_legend_lines(self, axes: list[Axes]) -> None:
        """Hide legend lines on all axes."""
        for ax in axes:
            if ax.get_legend():
                for line in ax.get_legend().get_lines():
                    line.set_visible(False)
