import os
import sys
import argparse
import json

from core.seq2seq.chatglm import ChatGLMSeq2Seq
from core.seq2seq.llama import LLAMASeq2Seq
from core.seq2seq.bloom import BLoomSeq2Seq
from core.seq2seq.qwen import QwenSeq2Seq
from core.seq2seq.baichuan import BaichuanSeq2Seq
from core.seq2seq.mixtral import MixtralSeq2Seq
from core.seq2seq.phi import PhiSeq2Seq
from core.seq2seq.gemma import GemmaSeq2Seq


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Finetune for all.')

    # base
    parser.add_argument('--data', type=str, default="data/train/", help='the data used for instructing tuning')
    parser.add_argument('--model_type', default="llama", choices=['llama', "llama2", 'llama3', 'chatglm', 'chatglm2', 'bloom', "qwen", "baichuan", "mixtral", "phi", "phi3", "gemma"])
    parser.add_argument('--labels', default="[\"0\", \"1\"]", help="Labels to classify, only used when task_type is classify")
    parser.add_argument('--model_path', default="LLMs/open-llama/openllama-3b", type=str)
    parser.add_argument('--output_dir', default="output/", type=str, help="The DIR to save the model")
    parser.add_argument('--disable_wandb', action="store_true", help="Disable report to wandb")

    # adapter
    parser.add_argument('--adapter', default="lora", choices=['lora', 'qlora', 'adalora', 'prompt', 'p_tuning', 'prefix'])
    parser.add_argument('--lora_r', default=8, type=int)
    parser.add_argument('--lora_alpha', default=16, type=int)
    parser.add_argument('--lora_dropout', default=0.05, type=float)
    parser.add_argument('--lora_target_modules', nargs='+',
                        help="the module to be injected, e.g. q_proj/v_proj/k_proj/o_proj for llama, query_key_value for bloom&GLM",
                        default=None)
    parser.add_argument('--adalora_init_r', default=12, type=int)
    parser.add_argument("--adalora_tinit", type=int, default=200,
                        help="number of warmup steps for AdaLoRA wherein no pruning is performed")
    parser.add_argument("--adalora_tfinal", type=int, default=1000,
                        help=" fix the resulting budget distribution and fine-tune the model for tfinal steps when using AdaLoRA ")
    parser.add_argument("--adalora_delta_t", type=int, default=10, help="interval of steps for AdaLoRA to update rank")
    parser.add_argument('--num_virtual_tokens', default=20, type=int)
    parser.add_argument('--mapping_hidden_dim', default=128, type=int)

    # train
    parser.add_argument('--epochs', default=3, type=int)
    parser.add_argument('--learning_rate', default=3e-4, type=float)
    parser.add_argument('--disable_warm_up', action="store_true")
    parser.add_argument('--cutoff_len', default=512, type=int)
    parser.add_argument('--val_set_size', default=0.2, type=float)
    parser.add_argument('--group_by_length', action="store_true")
    parser.add_argument('--logging_steps', default=20, type=int)

    parser.add_argument('--load_8bit', action="store_true")
    parser.add_argument('--add_eos_token', action="store_true")
    parser.add_argument('--resume_from_checkpoint', nargs='?', default=None, const=True,
                        help='resume from the specified or the latest checkpoint, e.g. `--resume_from_checkpoint [path]` or `--resume_from_checkpoint`')
    parser.add_argument('--per_gpu_train_batch_size', default=4, type=int, help='Batch size per GPU/CPU for training.')
    parser.add_argument('--gradient_accumulation_steps', default=32, type=int)
    parser.add_argument('--weight_decay', default=0, type=float)

    parser.add_argument('--fromdb', action="store_true")
    parser.add_argument('--db_iteration', default=None, type=str, help="The record's set name.")
    parser.add_argument('--db_item_num', default=0, type=int, help="The Limit Num of train/test items selected from DB.")

    args, _ = parser.parse_known_args()

    if args.model_type == "chatglm" or args.model_type == "chatglm2":
        llm = ChatGLMSeq2Seq()
    elif args.model_type == "llama" or args.model_type == "llama2" or args.model_type == "llama3":
        llm = LLAMASeq2Seq()
    elif args.model_type == "bloom":
        llm = BLoomSeq2Seq()
    elif args.model_type == "qwen":
        llm = QwenSeq2Seq()
    elif args.model_type == "baichuan":
        llm = BaichuanSeq2Seq()
    elif args.model_type == "mixtral":
        llm = MixtralSeq2Seq()
    elif args.model_type == "phi" or args.model_type == "phi3":
        llm = PhiSeq2Seq()
    elif args.model_type == "gemma":
        llm = GemmaSeq2Seq()
    else:
        print("model_type should be llama/llama2/llama3/bloom/chatglm/chatglm2/qwen/baichuan/mixtral/phi/phi3/gemma")
        sys.exit(-1)

    llm.data_path = args.data
    llm.model_type = args.model_type
    llm.task_type = args.task_type
    llm.labels = json.loads(args.labels)
    llm.base_model = args.model_path
    llm.output_dir = args.output_dir
    llm.disable_wandb = args.disable_wandb
    if llm.disable_wandb:
        os.environ["WANDB_DISABLED"] = "true"

    llm.adapter = args.adapter
    llm.lora_r = args.lora_r
    llm.lora_alpha = args.lora_alpha
    llm.lora_dropout = args.lora_dropout
    llm.lora_target_modules = args.lora_target_modules
    llm.adalora_init_r = args.adalora_init_r
    llm.adalora_tinit = args.adalora_tinit
    llm.adalora_tfinal = args.adalora_tfinal
    llm.adalora_delta_t = args.adalora_delta_t

    llm.num_virtual_tokens = args.num_virtual_tokens
    llm.mapping_hidden_dim = args.mapping_hidden_dim
    llm.epochs = args.epochs
    llm.learning_rate = args.learning_rate
    llm.disable_warm_up = args.disable_warm_up
    llm.cutoff_len = args.cutoff_len
    llm.val_set_size = args.val_set_size
    llm.group_by_length = args.group_by_length
    llm.logging_steps = args.logging_steps

    llm.load_8bit = args.load_8bit
    llm.add_eos_token = args.add_eos_token
    llm.resume_from_checkpoint = args.resume_from_checkpoint
    llm.per_gpu_train_batch_size = args.per_gpu_train_batch_size
    llm.gradient_accumulation_steps = args.gradient_accumulation_steps
    llm.weight_decay = args.weight_decay

    llm.fromdb = args.fromdb
    llm.db_iteration = args.db_iteration

    if not os.path.exists(llm.output_dir):
        os.makedirs(llm.output_dir)
        print("Warning: Directory {} Not Found, create automatically".format(llm.output_dir))

    if llm.adapter == "qlora" and sys.platform == "darwin":
        print("Unfortunately, SuperAdapters do not support qlora on Mac, please use lora/adalora instead")
        sys.exit(-1)

    llm.finetune()
