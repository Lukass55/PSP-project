const el = id => document.getElementById(id);

const euro = value =>
    Number(value).toLocaleString("lt-LT", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }) + " €";

let selectedData = null;
let currentTenantId = null;

function notify(text, kind = "danger", id = "globalMessage") {
    const node = el(id);
    node.textContent = text;
    node.className = `alert alert-${kind} mt-3`;
}

function clearNotice(id) {
    el(id).className = "d-none";
    el(id).textContent = "";
}

function showPage(page) {
    ["home", "manage"].forEach(p => {
        el(p + "Page").classList.toggle("d-none", p !== page);
    });

    document.querySelectorAll("[data-page]").forEach(button => {
        button.classList.toggle("active", button.dataset.page === page);
    });
}

function addOption(select, value, label) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    select.appendChild(option);
}

function clearGroup() {
    selectedData = null;
    el("totalExpenses").textContent = "—";
    el("positiveBalances").textContent = "—";
    el("activeGroup").textContent = "Nepasirinkta";
    el("memberCount").textContent = "Pasirinkite grupę";
    el("balancesList").replaceChildren();
    el("settlementsList").replaceChildren();
}

async function request(url, options) {
    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            typeof data.detail === "string"
                ? data.detail
                : "Užklausa nepavyko."
        );
    }

    return data;
}

// GRUPIŲ SĄRAŠAS
async function loadGroups(selectId = null) {
    const tenantId = currentTenantId;
    const select = el("groupId");

    clearGroup();
    select.replaceChildren();
    addOption(select, "", "Pasirinkite grupę");

    if (!tenantId) return;

    try {
        const groups = await request(`/tenants/${tenantId}/groups`);

        groups.forEach(group => {
            addOption(select, group.id, group.name);
        });

        if (groups.length === 0) {
            select.replaceChildren();
            addOption(select, "", "Dar neturite grupių");
        }

        if (selectId !== null) {
            select.value = String(selectId);
        }
    } catch (error) {
        notify("Nepavyko užkrauti grupių: " + error.message);
    }
}

// BALANSO EILUTĖ
function makeBalance(person) {
    const item = document.createElement("div");
    item.className = "balance-row";

    const left = document.createElement("div");
    left.className = "person";

    const avatar = document.createElement("span");
    avatar.className = "avatar";
    avatar.textContent = (person.name || "?").charAt(0).toUpperCase();

    const name = document.createElement("span");
    name.textContent = `${person.name} ${person.surname}`;

    left.append(avatar, name);

    const amount = document.createElement("strong");
    const balance = Number(person.balance);

    amount.className = balance >= 0 ? "amount-positive" : "amount-negative";
    amount.textContent = (balance > 0 ? "+" : "") + euro(balance);

    item.append(left, amount);
    return item;
}

// SKOLOS EILUTĖ
function makeSettlement(settlement) {
    const row = document.createElement("div");
    row.className = "settlement-row";

    const names = document.createElement("span");
    names.textContent =
        `${settlement.from_name} ${settlement.from_surname} → ` +
        `${settlement.to_name} ${settlement.to_surname}`;

    const amount = document.createElement("strong");
    amount.textContent = euro(settlement.amount);

    row.append(names, amount);
    return row;
}

// GRUPĖS BALANSAI
async function loadBalances() {
    const tenantId = currentTenantId;
    const groupId = el("groupId").value;

    clearNotice("globalMessage");

    if (!tenantId || !groupId) {
        notify("Pirmiausia pasirinkite grupę.");
        return;
    }

    try {
        const data = await request(
            `/tenants/${tenantId}/groups/${groupId}/balances`
        );

        selectedData = data;

        el("activeGroup").textContent = data.group_name;
        el("memberCount").textContent = `${data.balances.length} nariai`;

        const total = data.balances.reduce(
            (sum, person) => sum + Number(person.total_paid), 0
        );

        const positive = data.balances.reduce(
            (sum, person) => sum + Math.max(0, Number(person.balance)), 0
        );

        el("totalExpenses").textContent = euro(total);
        el("positiveBalances").textContent = euro(positive);

        const payer = el("payerId");
        const balances = el("balancesList");
        const settlements = el("settlementsList");

        payer.replaceChildren();
        balances.replaceChildren();
        settlements.replaceChildren();

        data.balances.forEach(person => {
            addOption(payer, person.user_id, `${person.name} ${person.surname}`);
            balances.append(makeBalance(person));
        });

        if (data.settlements.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty-state";
        empty.textContent = "Visi atsiskaitę!";

        settlements.append(empty);
        } else {
        data.settlements.forEach(settlement => {
        settlements.append(makeSettlement(settlement));
        });
        }

        showPage("home");

    } catch (error) {
        clearGroup();
        notify("Nepavyko parodyti balansų: " + error.message);
    }
}

// IŠLAIDŲ LANGAS
function openExpense() {
    if (!selectedData) {
        notify("Pirmiausia pasirinkite grupę ir spauskite „Rodyti“.");
        return;
    }

    clearNotice("expenseMessage");

    bootstrap.Modal.getOrCreateInstance(
        el("expenseModal")
    ).show();
}

el("groupId").addEventListener("change", clearGroup);

// NAUJOS IŠLAIDOS IŠSAUGOJIMAS
el("expenseForm").addEventListener("submit", async event => {
    event.preventDefault();

    const tenantId = currentTenantId;
    const groupId = el("groupId").value;

    try {
        await request(
            `/tenants/${tenantId}/groups/${groupId}/expenses`,
            {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    paid_by: Number(el("payerId").value),
                    amount: el("expenseAmount").value
                })
            }
        );

        el("expenseAmount").value = "";

        bootstrap.Modal.getOrCreateInstance(
            el("expenseModal")
        ).hide();

        await loadBalances();
        notify("Išlaida sėkmingai pridėta!", "success");

    } catch (error) {
        notify(error.message, "danger", "expenseMessage");
    }
});

// NAUJO VARTOTOJO KŪRIMAS
el("userForm").addEventListener("submit", async event => {
    event.preventDefault();

    const tenantId = currentTenantId;

    if (!tenantId) {
        notify("Nepavyko nustatyti prisijungusio vartotojo.", "danger", "userMessage");
        return;
    }

    try {
        const name = el("userName").value.trim();
        const surname = el("userSurname").value.trim();

        if (!name || !surname) {
            throw new Error("Įveskite vardą ir pavardę.");
        }

        await request(`/tenants/${tenantId}/users`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({name, surname})
        });

        await loadUsers();

        el("userName").value = "";
        el("userSurname").value = "";

        notify("Vartotojas sėkmingai sukurtas!", "success", "userMessage");

    } catch (error) {
        notify(error.message, "danger", "userMessage");
    }
});
async function loadUsers() {
    const tenantId = currentTenantId;
    const container = el("availableUsers");
    container.replaceChildren();

    if (!tenantId) {
        container.textContent = "Nepavyko nustatyti prisijungusio vartotojo.";
        return;
    }

    try {
        const users = await request(`/tenants/${tenantId}/users`);

        if (users.length === 0) {
            container.textContent = "Dar neturite pridėtų narių.";
            return;
        }

        users.forEach(user => {
            const label = document.createElement("label");
            label.className = "d-block mb-2";

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.className = "form-check-input me-2";
            checkbox.value = user.id;
            checkbox.name = "groupMember";

            label.append(
                checkbox,
                document.createTextNode(`${user.name} ${user.surname}`)
            );

            container.appendChild(label);
        });
    } catch (error) {
        notify(error.message, "danger", "groupMessage");
    }
}


el("groupForm").addEventListener("submit", async event => {
    event.preventDefault();

    const tenantId = currentTenantId;
    const name = el("newGroupName").value.trim();

    const memberIds = [
        ...document.querySelectorAll(
            'input[name="groupMember"]:checked'
        )
    ].map(input => Number(input.value));

    if (!tenantId) {
        notify("Nepavyko nustatyti prisijungusio vartotojo.", "danger", "groupMessage");
        return;
    }

    if (memberIds.length < 2) {
        notify(
            "Pasirinkite bent du grupės narius.",
            "danger",
            "groupMessage"
        );
        return;
    }

    try {
        const group = await request(
            `/tenants/${tenantId}/groups`,
            {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    name: name,
                    member_ids: memberIds
                })
            }
        );

        el("newGroupName").value = "";

        await loadGroups(group.id);
        await loadBalances();

        notify(
            "Grupė sėkmingai sukurta!",
            "success",
            "groupMessage"
        );

    } catch (error) {
        notify(error.message, "danger", "groupMessage");
    }
});
async function resetGroup() {
    const tenantId = currentTenantId;
    const groupId = el("groupId").value;

    if (!tenantId || !groupId) {
        notify(
            "Pirmiausia pasirinkite grupę.",
            "danger",
            "resetMessage"
        );
        return;
    }

    const groupName =
        el("groupId").selectedOptions[0].textContent;

    const confirmed = confirm(
        `Ar tikrai norite ištrinti visas grupės „${groupName}“ išlaidas?\n\n` +
        "Šio veiksmo atšaukti negalėsite."
    );

    if (!confirmed) return;

    try {
        const result = await request(
            `/tenants/${tenantId}/groups/${groupId}/expenses`,
            {method: "DELETE"}
        );

        await loadBalances();

        notify(
            `Grupė išvalyta. Ištrinta išlaidų: ${result.deleted_expenses}.`,
            "success",
            "globalMessage"
        );

    } catch (error) {
        notify(error.message, "danger", "resetMessage");
    }
}
// PRISIJUNGIMAS IR REGISTRACIJA

let authMode = "login";

function switchAuth(mode) {
    authMode = mode;

    document.getElementById("loginTab")
        .classList.toggle("active", mode === "login");

    document.getElementById("registerTab")
        .classList.toggle("active", mode === "register");

    document.getElementById("confirmPasswordBox")
        .classList.toggle("d-none", mode !== "register");

    document.getElementById("authSubmit").textContent =
        mode === "login" ? "Prisijungti" : "Sukurti paskyrą";

    document.getElementById("authPassword").autocomplete =
        mode === "login" ? "current-password" : "new-password";

    document.getElementById("authMessage").classList.add("d-none");
}

function showAuthMessage(message, isError = true) {
    const box = document.getElementById("authMessage");

    box.textContent = message;
    box.className = isError
        ? "alert alert-danger mt-3"
        : "alert alert-success mt-3";
}

async function showLoggedInApp(account) {
    document.getElementById("authScreen").classList.add("d-none");
    document.getElementById("appScreen").classList.remove("d-none");

    currentTenantId = account.tenant_id;
    if (!currentTenantId) {
        notify("Paskyra neturi priskirtos darbo erdvės.");
        return;
    }
    await loadGroups();
    await loadUsers();
}

async function logout() {
    try {
        const response = await fetch("/auth/logout", {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error("Nepavyko atsijungti");
        }

        document.getElementById("appScreen").classList.add("d-none");
        document.getElementById("authScreen").classList.remove("d-none");

        currentTenantId = null;
        clearGroup();
        el("groupId").replaceChildren();
        el("availableUsers").replaceChildren();
        document.getElementById("authForm").reset();
        switchAuth("login");

    } catch (error) {
        alert(error.message);
    }
}

async function checkLogin() {
    try {
        const response = await fetch("/auth/me");

        if (!response.ok) {
            throw new Error("Neprisijungęs");
        }

        const account = await response.json();
        await showLoggedInApp(account);

    } catch {
        document.getElementById("appScreen").classList.add("d-none");
        document.getElementById("authScreen").classList.remove("d-none");
    }
}

document.getElementById("authForm").addEventListener(
    "submit",
    async function(event) {
        event.preventDefault();

        const username = document.getElementById("authUsername").value.trim();
        const password = document.getElementById("authPassword").value;
        const confirmPassword =
            document.getElementById("authPasswordConfirm").value;

        if (authMode === "register" && password !== confirmPassword) {
            showAuthMessage("Slaptažodžiai nesutampa.");
            return;
        }

        const endpoint = authMode === "login"
            ? "/auth/login"
            : "/auth/register";

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({username, password})
            });

            const data = await response.json();

            if (!response.ok) {
                const detail = data.detail;
                throw new Error(
                    typeof detail === "string"
                        ? detail
                        : "Nepavyko atlikti veiksmo."
                );
            }

            if (authMode === "register") {
                switchAuth("login");
                showAuthMessage(
                    "Paskyra sukurta! Dabar prisijunkite.",
                    false
                );
                return;
            }

            await showLoggedInApp(data);

        } catch (error) {
            showAuthMessage(error.message);
        }
    }
);

// Patikriname sesiją atidarius puslapį
checkLogin();
