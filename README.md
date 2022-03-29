# Natureza Discreta - Conjuntos
Resolvedor de expressões de conjuntos através de entrada de dados.

# Contribuidores
* [@vmsou](https://github.com/vmsou)

## Sobre o Projeto
É um pequeno projeto pessoal, surgiu durante as aulas de Resolução de Problemas de Natureza Discreta em relação
a Teoria de Conjuntos, é capaz de ler uma entrada de dados, transformar em tokens e resolver a expressão.

Essa é uma lista dos recursos utilizados para fazer esse projeto
### 🛠 Construido utilizando
- Python 3.9 (sem bibliotecas externas)

## Principais Funcionalidades
### Operações
#### Conjuntos
- [x] União ("∪")
- [x] Interseção ("∩")
- [x] Diferença ("-")
- [x] Produto Cartesiano ("X")
- [x] Complemento (" ' ")
- [x] Diferença Simétrica ("⊕")
#### Pertencimento
- [x] Pertence ("∈")
- [x] Subconjunto Próprio ("⊂")
- [x] Subconjunto Impróprio ("⊆")
#### Outros
- [x] Definir Variável ("=")
- [x] Funções (como Potência: P(A))
- [x] Agrupamento ("(" e ")")


## Como executa-lo
Se você ter acesso a um terminal
```bash
cd conjuntos
```
```bash
python main.py
```

No terminal irá aparecer:
```bash
----------- [Set Calculator] -----------
Operations: ∪, ∩, -, ⊕, X, ', ⊂, ⊆, ∈
You can define variables. 
Example: 
> A = {1, 2}
Get the powerset of a set by calling P(A) or P({...})
You can also enter 'exit' to close program.
----------------------------------------

>
```
O simbolo '>' indica para entrar uma expressão. Assim como exemplo, podemos definir variáveis para conjuntos e manipula-los com operações.
```bash
> A = {1, 2, 3}
> B = {4, 5, 6}
> A ∪ B
{1, 2, 3, 4, 5, 6}
> A ∩ B
∅
```
## Status
<h4 align="center"> 
	🚧️ Em Desenvolvimento 🚧
</h4>

## Para fazer:
- [ ] Implementar Algoritimo Aho-Corasick para tokenizer
- [ ] Subconjunto Negado ("⊄")
- [ ] Superconjunto ("⊇")
- [ ] Não pertence ("∉")
