% Introduction to Metaheuristics - Local Search
% DrC. Alejandro Piad Morffis
% CC-BY - matcom.in/metaheuristics

# Review: Why optimization is hard

. . .

- Most interesting problems are NP-Hard
- Weak global structure.
- Disparate attraction basins.
- Most real-life functions are black-box.
- Function evaluation can be very costly.

# Review: What can we do

**Just search, but with common sense!**

- **Assume there is some local structure**: Near good solutions we can find other good solutions.
- **Approximate gradients:** Follow steps that improve the function fitness.
- **Avoid local optima:** Take measures to prevent getting stuck.

Any search method must balance between:

- **exploration** steps that lead you to discover new (and potentially better) attraction basins, and
- **exploitation** steps that lead you to improve your estimate of the best attraction basin.

# Back to the basics

**What is the simplest search method beyond random search?**

. . .

## Hill-climbing

- start with a random solution $x_i = x_0$
- while not finished:
  - sample a random solution $x_j$ _close to_ $x_i$
  - if $F(x_j) > F(x_i)$ then $x_{i+1} = x_j$
  - else $x_{i+1} = x_i$
- return $x_n$

. . .

## The devil is in the details

- When do we know we're done?
- What is _close enough_?

# Analyzing hill climbing {.t}

\vspace{1cm}

- start with a random solution $x_i = x_0$
- while not finished:
  - sample a random solution $x_j$ _close to_ $x_i$
  - if $F(x_j) > F(x_i)$ then $x_{i+1} = x_j$
  - else $x_{i+1} = x_i$
- return $x_n$

**How likely is to get stuck?**

. . .

**Theorem:** For any *fixed* value of closeness, hill climbing will eventually get stuck. (Why?)

# Analyzing hill climbing {.t}

\vspace{1cm}

- start with a random solution $x_i = x_0$
- while not finished:
  - sample a random solution $x_j$ _close to_ $x_i$
  - if $F(x_j) > F(x_i)$ then $x_{i+1} = x_j$
  - else $x_{i+1} = x_i$
- return $x_n$

**How to avoid geting stuck?**

# Fixing hill climbing {.t}

\vspace{1cm}

- start with a random solution $x_i = x_0$
- while not finished:
  - sample a random solution $x_j$ _close to_ $x_i$
  - if $F(x_j) > F(x_i)$ then $x_{i+1} = x_j$
  - else if $U(0,1) < \beta$ then $x_{i+1} = x_j$ **<-- here**
  - else $x_{i+1} = x_i$
- return $x^*$ _(best ever seen)_ **<-- and here**

**How to avoid geting stuck?**

Sometimes, take non-exploitative steps.

**What is the best value for $\beta$**

. . .

*A changing value...*

# Fixing hill climbing = Simulated annealing

- start with a random solution $x_i = x_0$
- set $\beta = \beta_0$ relatively high
- while not finished:
  - sample a random solution $x_j$ _close to_ $x_i$
  - if $F(x_j) > F(x_i)$ then $x_{i+1} = x_j$
  - else if $U(0,1) < \beta$ then $x_{i+1} = x_j$
  - else $x_{i+1} = x_i$
  - decrease $\beta$ _a little bit_ **<-- here**
- return $x^*$

**Ways to decrease $\beta$:**

. . .

- Linearly
- Exponentially
- Only if no improvement
- . . .

# Simulated annealing

**How good is this?**

- If the probability of sampling any solution $x_j$ from the current $x_i$ is never zero
- And the "cooling schedule" is _sufficiently slow_
- Then SA converges to a global optima _eventually_!

. . .

**Improvements**

- Decrease the size of the vicinity iteratively
- Make the probability of choosing a solution $x_j$ proportional to how good it is compared to $x_i$
- Restart $\beta$ after some iterations stuck