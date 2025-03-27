#!/usr/bin/env python3
import click
from cli.bad_scanner import main

@click.command()
@click.argument('input_pdf', type=click.Path(exists=True, readable=True))
@click.argument('output_pdf', type=click.Path(writable=True))
@click.option('--blur-radius', '-b', type=float, default=2.0, help='Gaussian blur radius')
@click.option('--dust-density', '-d', type=float, default=1.0, help='Multiplier for dust spot density')
@click.option('--dust-min-radius', type=int, default=1, help='Minimum radius for dust spots')
@click.option('--dust-max-radius', type=int, default=5, help='Maximum radius for dust spots')
@click.option('--dust-alpha-min', type=int, default=30, help='Minimum alpha for dust spots')
@click.option('--dust-alpha-max', type=int, default=100, help='Maximum alpha for dust spots')
@click.option('--scratch-count', '-s', type=int, default=3, help='Number of scratches')
@click.option('--scratch-line-width-min', type=int, default=1, help='Minimum scratch line width')
@click.option('--scratch-line-width-max', type=int, default=3, help='Maximum scratch line width')
@click.option('--scratch-alpha-min', type=int, default=50, help='Minimum alpha for scratches')
@click.option('--scratch-alpha-max', type=int, default=150, help='Maximum alpha for scratches')
@click.option('--contrast', '-c', type=float, default=1.0, help='Contrast factor for the final image')
@click.option('--sharpness', '-S', type=float, default=1.0, help='Sharpness factor for the final image')
@click.option('--brightness', '-B', type=float, default=1.0, help='Brightness factor for the final image')
@click.option('--rotate', '-r', type=float, default=0.0, help='Rotation angle in degrees for the final image')
@click.option('--seed', type=int, default=None, help='Random seed for consistent overlay generation')

def bad_scanner_cli(input_pdf, output_pdf, blur_radius, dust_density, dust_min_radius, dust_max_radius,
                 dust_alpha_min, dust_alpha_max, scratch_count, scratch_line_width_min,
                 scratch_line_width_max, scratch_alpha_min, scratch_alpha_max, contrast,
                 sharpness, brightness, rotate, seed):
    """
    Process a PDF file to simulate an out-of-focus scanner with dirty glass effect.
    
    INPUT_PDF is the path to the PDF file to process.
    OUTPUT_PDF is the path where the processed PDF will be saved.
    """
    main(
        input_pdf, output_pdf,
        blur_radius=blur_radius,
        dust_density=dust_density,
        dust_min_radius=dust_min_radius,
        dust_max_radius=dust_max_radius,
        dust_alpha_min=dust_alpha_min,
        dust_alpha_max=dust_alpha_max,
        scratch_count=scratch_count,
        scratch_line_width_min=scratch_line_width_min,
        scratch_line_width_max=scratch_line_width_max,
        scratch_alpha_min=scratch_alpha_min,
        scratch_alpha_max=scratch_alpha_max,
        contrast=contrast,
        sharpness=sharpness,
        brightness=brightness,
        rotate=rotate,
        seed=seed
    )

if __name__ == '__main__':
    bad_scanner_cli()
