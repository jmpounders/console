from typing import Any

from console.components.base import Component, Container, Text, VStack, LinePlot


class TextInBorder(Component):

    def __init__(
            self,
            data: list[str],
            text_params: dict[str, Any],
            container_params: dict[str, Any]
        ):

        data_fields = [
            Text(item, **text_params)
            for item in data
        ]

        vstack = VStack(data_fields, container_params['background_color'], 10)

        pad_amount = 2 * (container_params['child_padding'] + container_params['border_margin'])
        width, height = vstack.width + pad_amount, vstack.height + pad_amount
        self.component = Container(width, height, [vstack], **container_params)
        super().__init__(self.component.width, self.component.height)

    def get_surface(self):
        return self.component.get_surface()


class AnnotatedLinePlots(Component):

    def __init__(
            self,
            labels: list[str],
            x_data: list[float],
            y_datas: list[list[float]],
            text_params: dict[str, Any],
            container_params: dict[str, Any]
        ):

        plots = []
        plot_container_params = {
            'border_thickness': 0,
            'border_radius': 0,
            'border_margin': 0,
            'border_color': container_params['background_color'],
            'background_color': container_params['background_color'],
            'child_padding': 0,
        }
        small_text_params = {key: value for key, value in text_params.items()}
        small_text_params['font_size'] = text_params['font_size']//2
        for label, y_data in zip(labels, y_datas):
            label_comp = Text(label, **text_params)

            try:
                annotations = [min(y_data), sum(y_data)/len(y_data), max(y_data)]
            except:
                annotations = [0, 0, 0]
            # values = VStack(
            #     [Text(f'{y:.2f}', **text_params) for y in annotations],
            #     text_params['font_background'],
            #     padding=2
            # )
            values_comp = Text(
                f'{"/".join([f"{y:.0f}" for y in annotations])}',
                **small_text_params
            )

            height = max([label_comp.height, values_comp.height])

            plot = LinePlot(
                300,
                height,
                x_data,
                y_data,
                container_params['background_color'],
                container_params['border_color'],
                x_padding = 5,
                y_padding = 2
            )

            # height += 2*container_params['child_padding']
            width = label_comp.width + values_comp.width + plot.width
            # width += 2*container_params['child_padding']

            plots.append(Container(
                width,
                height,
                [label_comp, plot, values_comp],
                **plot_container_params
            ))

        self.plots_component = VStack(plots, container_params['background_color'], 5)

        height = self.plots_component.height + 2*container_params['border_margin'] + 2*container_params['child_padding']
        width = self.plots_component.width + 2*container_params['border_margin'] + 2*container_params['child_padding']
        self.component = Container(width, height, [self.plots_component], **container_params)
        super().__init__(width, height)

    def get_surface(self):
        return self.component.get_surface()