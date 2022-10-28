#!/usr/bin/env python
"""
Performs basic cleaning on the data and save the results in Weights & Biases
"""
import argparse
import os
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    ######################
    logger.info(f'Downloading artifact {args.input_artifact}')
    artifact_local_path = run.use_artifact(args.input_artifact).file()  

    # Read the data from the artifact
    logger.info("Loading DataFrame")
    df = pd.read_csv(artifact_local_path)

    # Remove outliers
    logger.info('Drop outliers and convert datetime')
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()
    df['last_review'] = pd.to_datetime(df['last_review'])
        # Save dataframe
    logger.info(f'Saving Dataframe {args.output_artifact}')
    df.to_csv('clean_sample.csv', index=False)

    # Create an W&B artifact object
    logger.info('Creating artifact object')
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )

    artifact.add_file(local_path='clean_sample.csv')

    # Upload the artifact to the run and tag it as reference
    logger.info(f'Logging artifact {args.output_artifact}')
    run.log_artifact(artifact)

    # Finish Run
    os.remove(args.output_artifact)
    run.finish()
    ######################


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="this step cleans the data")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Input artifact name",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Output artifact name",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="Output artifact type",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Output artifact description",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=int,
        help="Minimum price limit",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=int,
        help="Maximum price limit",
        required=True
    )

    args = parser.parse_args()

    go(args)
