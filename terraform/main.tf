data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}

# ---------------- network ----------------
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.1"

  name = "clinicflow-vpc"
  cidr = var.vpc_cidr
  azs  = local.azs

  # two public subnets (load balancers, NAT) and two private subnets (worker nodes)
  public_subnets  = ["10.30.101.0/24", "10.30.102.0/24"]
  private_subnets = ["10.30.1.0/24", "10.30.2.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = true # one NAT keeps the student bill low
  enable_dns_hostnames = true

  # let the AWS load balancer controller / ingress find the right subnets
  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
  }
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = 1
  }
}

# ---------------- EKS ----------------
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.37.1"

  cluster_name    = var.cluster_name
  cluster_version = var.kubernetes_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access           = true
  enable_cluster_creator_admin_permissions = true

  eks_managed_node_groups = {
    general = {
      instance_types = var.node_instance_types
      min_size       = var.node_min_size
      desired_size   = var.node_desired_size
      max_size       = var.node_max_size
      labels = {
        workload = "clinicflow"
      }
    }
  }
}
