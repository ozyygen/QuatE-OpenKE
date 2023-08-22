from config import Trainer, Tester
from module.model.QuantE import QuantE
from module.loss import SoftplusLoss
from module.strategy import NegativeSampling
from data import TrainDataLoader, TestDataLoader

# dataloader for training
train_dataloader = TrainDataLoader(
	in_path = "./benchmarks/FB13/", 
	nbatches = 100,
	threads = 8, 
	sampling_mode = "normal", 
	bern_flag = 1, 
	filter_flag = 1, 
	neg_ent = 25,
	neg_rel = 0
)

# dataloader for test
test_dataloader = TestDataLoader("./benchmarks/FB13/", "link")

# define the model
quantE = QuantE(
	ent_tot = train_dataloader.get_ent_tot(),
	rel_tot = train_dataloader.get_rel_tot(),
	dim = 200
)

# define the loss function
model = NegativeSampling(
	model = quantE, 
	loss = SoftplusLoss(),
	batch_size = train_dataloader.get_batch_size(), 
	regul_rate = 1.0
)
print(train_dataloader.get_batch_size())
# train the model
trainer = Trainer(model = model, data_loader = train_dataloader, alpha = 0.5, use_gpu = False, checkpoint_dir="./checkpoint/",opt_method = "adagrad")
trainer.run()

quantE.save_checkpoint('./checkpoint/quantE.ckpt')

# test the model
quantE.load_checkpoint('./checkpoint/quantE.ckpt')
tester = Tester(model = quantE, data_loader = test_dataloader, use_gpu = False)
tester.run_link_prediction(type_constrain = False)