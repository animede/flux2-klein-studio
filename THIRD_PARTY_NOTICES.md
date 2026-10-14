# Third-party models and licenses

This repository contains application source code. It does **not** distribute model
weights. The `models/` directory and generated images are excluded from Git.

The repository's [Apache License 2.0](LICENSE) applies only to the application code
authored for Klein Reference Studio. It does not grant rights to model weights,
model names, third-party software, or generated content. The controlling license is
always the license published by each provider.

## FLUX.2 klein 4B

- Base model: [black-forest-labs/FLUX.2-klein-4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)
- Quantized model: [unsloth/FLUX.2-klein-4B-GGUF](https://huggingface.co/unsloth/FLUX.2-klein-4B-GGUF)
- License: Apache License 2.0, as stated on those distribution pages.

Apache-2.0 permits commercial use subject to its terms, including preservation of
required copyright, license, and notice information when redistributing covered
material. Review the provider pages before use because their contents may change.

## FLUX.2 klein 9B

- Base model: [black-forest-labs/FLUX.2-klein-9B](https://huggingface.co/black-forest-labs/FLUX.2-klein-9B)
- Quantized model: [unsloth/FLUX.2-klein-9B-GGUF](https://huggingface.co/unsloth/FLUX.2-klein-9B-GGUF)
- License: [FLUX Non-Commercial License v2.1](https://huggingface.co/black-forest-labs/FLUX.2-klein-9B/blob/main/LICENSE.txt)
- Usage rules: [Black Forest Labs Usage Policy](https://bfl.ai/legal/usage-policy)

The 9B model and its GGUF derivative are not covered by this repository's
Apache-2.0 license. Their model license limits use to non-commercial and
non-production purposes and contains additional restrictions. Among other things,
the license requires output filtering or review before outputs are displayed or
distributed, and may require disclosure that content is AI-generated. Read the
complete current terms before downloading or using 9B. The output-related clauses
do not turn operation of the 9B model into permitted commercial or production use.

The downloader therefore requires an explicit `--acknowledge-9b-license` option and
uses the official gated base repository. The option records only the operator's
acknowledgement; it does not replace acceptance on Hugging Face and does not modify
the license. An access token for an account that has accepted the official access
terms may be required.

Do not redistribute 9B weights or derivatives without complying with the license's
redistribution, attribution, notice, and downstream-license requirements. This
repository deliberately does not include those files.

## Python packages

Packages installed from `requirements.txt` remain under their respective licenses.
They are downloaded from their package providers and are not relicensed by this
repository. Use `pip show <package>` and the linked upstream project when reviewing
a specific dependency.

## Names and marks

FLUX and Black Forest Labs names and marks belong to their respective owners. This
project is an independent integration and is not affiliated with or endorsed by
Black Forest Labs, Hugging Face, or Unsloth.

This notice is a practical summary, not a substitute for the license texts. If a
summary conflicts with a provider's terms, the provider's terms control.
