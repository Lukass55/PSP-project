const el = id => document.getElementById(id);

const euro = value =>
    Number(value).toLocaleString("lt-LT", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }) + " €";

let selectedData = null;
let currentAccount = null;
let authMode = "login";

function notify(text, kind = "danger", id = "globalMessage") {
    const node = el(id);
    if (!node) return;
    node.textContent = text;
    node.className = `alert alert-${kind} mt-3`;
}

function clearNotice(id) {
    const node = el(id);
    if (!node) return;
    node.className = "d-none";
    node.textContent = "";
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
    el("payerId").replaceChildren();
}

async function request(url, options = {}) {
    const response = await fetch(url, {
        credentials: "same-origin",
        ...options
    });

    const data = await response.json();

    if (!response.ok) {
        const detail = data.detail;
        throw new Error(typeof detail === "string" ? detail : "Užklausa nepavyko.");
    }

    return data;
}

async function loadGroups(selectId = null) {
    const select = el("groupId");
    clearGroup();
    select.replaceChildren();
    addOption(select, "", "Pasirinkite grupę");

    try {
        const groups = await request("/groups");

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

function makeSettlement(settlement) {
    const row = document.createElement("div");
    row.className = "settlement-row";

    const names = document.createElement("span");
    names.textContent = `${settlement.from_name} ${settlement.from_surname} → ${settlement.to_name} ${settlement.to_surname}`;

    const amount = document.createElement("strong");
    amount.textContent = euro(settlement.amount);

    row.append(names, amount);
    return row;
}

async function loadBalances() {
    const groupId = el("groupId").value;
    clearNotice("globalMessage");

    if (!groupId) {
        notify("Pirmiausia pasirinkite grupę.");
        return;
    }

    try {
        const data = await request(`/groups/${groupId}/balances`);
        selectedData = data;

        el("activeGroup").textContent = data.group_name;
        el("memberCount").textContent = `${data.balances.length} nariai`;

        const total = data.balances.reduce((sum, person) => sum + Number(person.total_paid), 0);
        const positive = data.balances.reduce((sum, person) => sum + Math.max(0, Number(person.balance)), 0);

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

function openExpense() {
    if (!selectedData) {
        notify("Pirmiausia pasirinkite grupę ir spauskite „Rodyti“.");
        return;
    }

    clearNotice("expenseMessage");
    bootstrap.Modal.getOrCreateInstance(el("expenseModal")).show();
}

el("groupId").addEventListener("change", clearGroup);

el("expenseForm").addEventListener("submit", async event => {
    event.preventDefault();
    const groupId = el("groupId").value;

    try {
        await request(`/groups/${groupId}/expenses`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                paid_by: Number(el("payerId").value),
                amount: el("expenseAmount").value
            })
        });

        el("expenseAmount").value = "";
        bootstrap.Modal.getOrCreateInstance(el("expenseModal")).hide();
        await loadBalances();
        notify("Išlaida sėkmingai pridėta!", "success");
    } catch (error) {
        notify(error.message, "danger", "expenseMessage");
    }
});

el("userForm").addEventListener("submit", async event => {
    event.preventDefault();

    try {
        const name = el("userName").value.trim();
        const surname = el("userSurname").value.trim();

        if (!name || !surname) {
            throw new Error("Įveskite vardą ir pavardę.");
        }

        await request("/users", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, surname })
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
    const container = el("availableUsers");
    container.replaceChildren();

    try {
        const users = await request("/users");
        const otherUsers = users.filter(user => user.id !== currentAccount?.user_id);

        if (otherUsers.length === 0) {
            container.textContent = "Pridėkite bent vieną kitą žmogų.";
            return;
        }

        otherUsers.forEach(user => {
            const label = document.createElement("label");
            label.className = "d-block mb-2";

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.className = "form-check-input me-2";
            checkbox.value = user.id;
            checkbox.name = "groupMember";

            label.append(checkbox, document.createTextNode(`${user.name} ${user.surname}`));
            container.appendChild(label);
        });
    } catch (error) {
        notify(error.message, "danger", "groupMessage");
    }
}

el("groupForm").addEventListener("submit", async event => {
    event.preventDefault();
    const name = el("newGroupName").value.trim();
    const memberIds = [...document.querySelectorAll('input[name="groupMember"]:checked')].map(input => Number(input.value));

    if (!name) {
        notify("Įveskite grupės pavadinimą.", "danger", "groupMessage");
        return;
    }

    if (memberIds.length < 1) {
        notify("Pasirinkite bent vieną papildomą narį.", "danger", "groupMessage");
        return;
    }

    try {
        const group = await request("/groups", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, member_ids: memberIds })
        });

        el("newGroupName").value = "";
        document.querySelectorAll('input[name="groupMember"]:checked').forEach(input => {
            input.checked = false;
        });

        await loadGroups(group.id);
        await loadBalances();
        notify("Grupė sėkmingai sukurta!", "success", "groupMessage");
    } catch (error) {
        notify(error.message, "danger", "groupMessage");
    }
});

async function resetGroup() {
    const groupId = el("groupId").value;

    if (!groupId) {
        notify("Pirmiausia pasirinkite grupę.", "danger", "resetMessage");
        return;
    }

    const groupName = el("groupId").selectedOptions[0].textContent;
    const confirmed = confirm(`Ar tikrai norite ištrinti visas grupės „${groupName}“ išlaidas?\n\nŠio veiksmo atšaukti negalėsite.`);

    if (!confirmed) return;

    try {
        const result = await request(`/groups/${groupId}/expenses`, { method: "DELETE" });
        await loadBalances();
        notify(`Grupė išvalyta. Ištrinta išlaidų: ${result.deleted_expenses}.`, "success", "globalMessage");
    } catch (error) {
        notify(error.message, "danger", "resetMessage");
    }
}

function switchAuth(mode) {
    authMode = mode;
    el("loginTab").classList.toggle("active", mode === "login");
    el("registerTab").classList.toggle("active", mode === "register");
    el("registerFields").classList.toggle("d-none", mode !== "register");
    el("confirmPasswordBox").classList.toggle("d-none", mode !== "register");
    el("authSubmit").textContent = mode === "login" ? "Prisijungti" : "Sukurti paskyrą";
    el("authPassword").autocomplete = mode === "login" ? "current-password" : "new-password";
    el("authPassword").minLength = mode === "login" ? 1 : 8;
    el("authName").required = mode === "register";
    el("authSurname").required = mode === "register";
    el("authPasswordConfirm").required = mode === "register";
    clearNotice("authMessage");
}

function showAuthMessage(message, isError = true) {
    const box = el("authMessage");
    box.textContent = message;
    box.className = isError ? "alert alert-danger mt-3" : "alert alert-success mt-3";
}

async function showLoggedInApp(account) {
    currentAccount = account;
    el("authScreen").classList.add("d-none");
    el("appScreen").classList.remove("d-none");
    clearNotice("globalMessage");
    await loadGroups();
    await loadUsers();
}

async function logout() {
    try {
        await request("/auth/logout", { method: "POST" });
        currentAccount = null;
        el("appScreen").classList.add("d-none");
        el("authScreen").classList.remove("d-none");
        clearGroup();
        el("groupId").replaceChildren();
        el("availableUsers").replaceChildren();
        el("authForm").reset();
        showPage("home");
        switchAuth("login");
    } catch (error) {
        alert(error.message);
    }
}

async function checkLogin() {
    try {
        const account = await request("/auth/me");
        await showLoggedInApp(account);
    } catch {
        currentAccount = null;
        el("appScreen").classList.add("d-none");
        el("authScreen").classList.remove("d-none");
    }
}

el("authForm").addEventListener("submit", async event => {
    event.preventDefault();

    const username = el("authUsername").value.trim();
    const password = el("authPassword").value;
    const name = el("authName").value.trim();
    const surname = el("authSurname").value.trim();
    const confirmPassword = el("authPasswordConfirm").value;

    if (authMode === "register") {
        if (!name || !surname) {
            showAuthMessage("Įveskite vardą ir pavardę.");
            return;
        }
        if (password !== confirmPassword) {
            showAuthMessage("Slaptažodžiai nesutampa.");
            return;
        }
    }

    const endpoint = authMode === "login" ? "/auth/login" : "/auth/register";
    const payload = { username, password };

    if (authMode === "register") {
        payload.name = name;
        payload.surname = surname;
    }

    try {
        await request(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (authMode === "register") {
            el("authForm").reset();
            switchAuth("login");
            showAuthMessage("Paskyra sukurta! Dabar prisijunkite.", false);
            return;
        }

        const account = await request("/auth/me");
        await showLoggedInApp(account);
    } catch (error) {
        showAuthMessage(error.message);
    }
});

checkLogin();